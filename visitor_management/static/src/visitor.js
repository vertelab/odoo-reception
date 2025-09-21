/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { VisitorForm } from "@visitor/visitor_form/visitor_form";
import { WelcomePage } from "@visitor/welcome_page/welcome_page";
import { RegisterPage } from "@visitor/register_page/register_page";
import { DrinkPage } from "@visitor/drink_page/drink_page";
import { Navbar } from "@visitor/navbar/navbar";
import { HostPage } from "@visitor/host_page/host_page";
import { EndPage } from "@visitor/end_page/end_page";
import { QuickCheckIn } from "@visitor/quick_check_in/quick_check_in";

import { Component, useState, onWillStart, markup } from "@odoo/owl";

export class visitor extends Component {
    static template = "visitor.visitor";
    static components = {
        WelcomePage,
        Navbar,
        VisitorForm,
        QuickCheckIn,
        HostPage,
        RegisterPage,
        DrinkPage,
        EndPage,
    };
    static props = {
        id: Number,
        isMobile: Boolean,
        currentLang: String,
    };
    setup() {
        this.state = useState({
            currentComponent: !this.props.isMobile ? WelcomePage : VisitorForm,
            plannedVisitors: [],
        });
        const urlToken = window.location.href.split("/").findLast((s) => s);
        this.token = urlToken.includes("?") ? urlToken.split("?")[0] : urlToken;
        this.visitorUrl = `/visitor/${this.props.id}/${this.token}`;
        onWillStart(this.onWillStart);
        if (this.props.isMobile) {
            // Retrieve the saved component from sessionStorage
            const savedComponent = sessionStorage.getItem("currentComponent");
            if (savedComponent) {
                const component = registry.category("visitor_screens").get(savedComponent);
                this.state.currentComponent = component;
            }
            window.addEventListener("beforeunload", () => {
                // Before the page refresh, save the current component to sessionStorage
                sessionStorage.setItem("currentComponent", this.state.currentComponent.name);
            });
        }
    }

    async onWillStart() {
        this.visitorData = await rpc(`${this.visitorUrl}/get_visitor_data`);
        this.station = this.visitorData.station[0];
    }

    /* This method updates the plannedVisitors */
    updatePlannedVisitors() {
        this._getPlannedVisitors();
        this.intervalId = setInterval(() => this._getPlannedVisitors(), 600000); // 10 minutes
    }

    /**
     * Get the plannedVisitors from the backend through rpc call
     *
     * @private
     */
    async _getPlannedVisitors() {
        this.state.plannedVisitors = await rpc(`${this.visitorUrl}/get_planned_visitors`);
    }

    /* This method creates the visitor in the backend through rpc call */
    async createVisitor() {
        const result = await rpc(`${this.visitorUrl}/prepare_visitor_data`, {
            name: this.visitorData.visitorName,
            phone: this.visitorData.visitorPhone,
            email: this.visitorData.visitorEmail,
            company: this.visitorData.visitorCompany,
            host_ids: this.hostData ? [this.hostData.hostId] : [],
        });
        this.visitorId = result.visitor_id;
    }

    onClose() {
        // Check if the device is mobile or not and show the screen accordingly
        !this.props.isMobile ? this.showScreen("WelcomePage") : this.showScreen("VisitorForm");
    }

    /**
     * @param {Event} ev
     */
    onChangeLang(ev) {
        window.location.href = window.location.pathname + `?lang=${encodeURIComponent(ev.currentTarget.value)}`;
    }

    /**
     * This method change the current screen
     *
     * @param {string} name
     */
    showScreen(name) {
        const component = registry.category("visitor_screens").get(name);
        this.state.currentComponent = component;
    }

    /* This method clears the interval for updatePlannedVisitors */
    clearUpdatePlannedVisitors() {
        clearInterval(this.intervalId);
    }

    /* Reset the data */
    resetData() {
        this.hostData = null;
        this.visitorData = null;
        this.plannedVisitorData = null;
        this.isDrinkSelected = false;
    }

    /**
     * @param {string} name
     * @param {string|false} phone
     * @param {string|false} email
     * @param {string|false} company
     */
    setVisitorData(name, phone, email, company) {
        this.visitorData = {
            visitorName: name,
            visitorPhone: phone,
            visitorEmail: email,
            visitorCompany: company,
        };
    }

    /**
     * @param {Object} host
     */
    setHostData(host) {
        this.hostData = {
            hostId: host.id,
            hostName: host.display_name,
        };
    }

    /**
     * @param {number} plannedVisitorId
     * @param {string|false} plannedVisitorMessage
     * @param {Array} plannedVisitorHosts
     */
    setPlannedVisitorData(plannedVisitorId, plannedVisitorMessage, plannedVisitorHosts) {
        this.plannedVisitorData = {
            plannedVisitorId: plannedVisitorId,
            plannedVisitorMessage: plannedVisitorMessage,
            plannedVisitorHosts: plannedVisitorHosts,
        };
    }

    /**
     * @param {boolean} boolean
     */
    setDrink(boolean) {
        this.isDrinkSelected = boolean;
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    get visitorProps() {
        let props = {};
        if (this.state.currentComponent === WelcomePage) {
            props = {
                showScreen: this.showScreen.bind(this),
                resetData: this.resetData.bind(this),
                onChangeLang: this.onChangeLang.bind(this),
                token: this.token,
                companyName: this.visitorData.company.name,
                stationInfo: this.station,
                langs: this.visitorData.langs.length > 1 ? this.visitorData.langs : false,
                currentLang: this.props.currentLang,
            };
        } else if (this.state.currentComponent === VisitorForm) {
            props = {
                onChangeLang: this.onChangeLang.bind(this),
                showScreen: this.showScreen.bind(this),
                clearUpdatePlannedVisitors: this.clearUpdatePlannedVisitors.bind(this),
                setVisitorData: this.setVisitorData.bind(this),
                updatePlannedVisitors: this.updatePlannedVisitors.bind(this),
                visitorData: this.visitorData || false,
                isMobile: this.props.isMobile,
                currentComponent: this.state.currentComponent.name,
                isPlannedVisitors: this.state.plannedVisitors.length ? true : false,
                stationInfo: this.station,
                langs: this.visitorData.langs.length > 1 ? this.visitorData.langs : false,
                currentLang: this.props.currentLang,
                theme: this.station.theme,
            };
        } else if (this.state.currentComponent === HostPage) {
            props = {
                stationId: this.station.id,
                token: this.token,
                showScreen: this.showScreen.bind(this),
                setHostData: this.setHostData.bind(this),
            };
        } else if (this.state.currentComponent === RegisterPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                onClose: this.onClose.bind(this),
                createVisitor: this.createVisitor.bind(this),
                theme: this.station.theme,
                isMobile: this.props.isMobile,
                isDrinkVisible: this.visitorData.drinks?.length ? true : false,
                plannedVisitorData: this.plannedVisitorData,
                hostData: this.hostData,
            };
        } else if (this.state.currentComponent === DrinkPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                setDrink: this.setDrink.bind(this),
                theme: this.station.theme,
                drinkInfo: this.visitorData.drinks,
                stationId: this.props.id,
                token: this.token,
                visitorId: this.plannedVisitorData
                    ? this.plannedVisitorData.plannedVisitorId
                    : this.visitorId,
            };
        } else if (this.state.currentComponent === EndPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                onClose: this.onClose.bind(this),
                isMobile: this.props.isMobile,
                isDrinkSelected: this.isDrinkSelected,
                theme: this.station.theme,
                plannedVisitorData: this.plannedVisitorData,
                hostData: this.hostData,
            };
        }
        return props;
    }

    get navBarProps() {
        return {
            showScreen: this.showScreen.bind(this),
            currentComponent: this.state.currentComponent.name,
            companyInfo: this.visitorData.company,
            isMobile: this.props.isMobile,
            isPlannedVisitors: this.state.plannedVisitors.length ? true : false,
            theme: this.station.theme,
            onChangeLang: this.onChangeLang.bind(this),
            langs: this.visitorData.langs.length > 1 ? this.visitorData.langs : false,
            currentLang: this.props.currentLang,
        };
    }

    get quickCheckInProps() {
        return {
            setPlannedVisitorData: this.setPlannedVisitorData.bind(this),
            showScreen: this.showScreen.bind(this),
            stationId: this.props.id,
            token: this.token,
            plannedVisitors: this.state.plannedVisitors,
            theme: this.station.theme,
        };
    }

    get markupValue() {
        return markup(this.station.description);
    }
}

registry.category("public_components").add("visitor", visitor);
