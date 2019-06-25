import React from 'react';
import './css/app-name-title.css';
/*
Functional component to display the greeting
 */
const AppNameTitle = () => {
    return (
        <div className={'appTitle'}>{process.env.REACT_APP_NAME_TITLE}</div>
    );
};
export default AppNameTitle;