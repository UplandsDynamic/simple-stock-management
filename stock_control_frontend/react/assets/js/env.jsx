import React from "react";

const Env = () => {
    return {
        /* LOCAL DEV */
        apiRoot: 'http://localhost:3000/api',
        apiDataRoot: 'http://localhost:3000/api/v1',
        appDetails: {
            organisationName: 'Simple Stock Management, from Aninstance.com',
            shortOrgName: 'Simple Stock Management',
            copyright:
                (<div><p>Application developed by Aninstance Consultancy. <a
                    href="https://www.aninstance.com" target="_blank">Tap here for support enquiries</a>.
                    <br/>Version: 1.0.6</p>
                </div>),
            footerText: `My custom footer text ...`,
            greeting: (<span>My custom greeting ...</span>)
        }
    };
};

export default Env;