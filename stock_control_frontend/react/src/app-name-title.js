import React from 'react'
import './css/app-name-title.css'
/*
Functional component to display the greeting
 */
const AppNameTitle = () => {
    return (
        <div className={'container'}>
            <div className={'row'}>
                <div className={'col-12'}>
                    <span className={'appTitle'}>{process.env.REACT_APP_NAME_TITLE}</span>
                </div>
            </div>
        </div>
    );
};
export default AppNameTitle;