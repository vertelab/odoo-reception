/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, markup } from "@odoo/owl";
import { useInactivity } from "../use_inactivity";

export class EndPage extends Component {
    static template = "reception.EndPage";
    static props = {
        hostData: { optional: true },
        isMobile: Boolean,
        onClose: Function,
        plannedVisitorData: { optional: true },
        showScreen: Function,
        theme: String,
    };
    setup() {
        if (!this.props.isMobile) {
            useInactivity(() => this.props.onClose(), 15000);
        }
    }

    get markupValue() {
        return markup(this.props.plannedVisitorData?.plannedVisitorMessage);
    }
}

registry.category("reception_screens").add("EndPage", EndPage);
