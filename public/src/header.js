import boxLogo from './img/box.svg'
import './css/header.css';
import AppNameTitle from './app-name-title';
import LoginForm from './loginform';
import React from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Header = ({
    authMeta = {}, apiOptions = null, csrfToken = null, setMessage, getSessionStorage, setSessionStorage,
    deleteSessionStorage, setAuthentication, openTruck, accountModes, setAccountMode, accountMode
} = {}) => {

    const storeAccount = accountMode === accountModes.WAREHOUSE

    const buttons = (<div className={'btn-group d-flex'} role={'group'}>
        <button className={'btn btn-lg btn-primary'}
            onClick={(e) => {
                e.preventDefault();
                setAccountMode()
            }}><FontAwesomeIcon icon={"user-circle"} />
        </button>
        <button className={'btn btn-lg btn-success'}
            disabled={!storeAccount}
            onClick={(e) => {
                e.preventDefault();
                openTruck({ state: true })
            }}><FontAwesomeIcon icon={"truck"} />
        </button>
    </div>);
    return (
        <React.Fragment>
            <div className={'header d-flex flex-row-reverse header'}>
                {authMeta.authenticated ? buttons : ''}
                <LoginForm authMeta={authMeta}
                    apiOptions={apiOptions}
                    csrfToken={csrfToken}
                    setMessage={setMessage}
                    getSessionStorage={getSessionStorage}
                    setSessionStorage={setSessionStorage}
                    deleteSessionStorage={deleteSessionStorage}
                    setAuthentication={setAuthentication}
                />
                <div className={'d-flex flex-fill'}>
                    <img className={'logo m-1'} src={boxLogo} alt={'Box logo'} />
                    <div className={'account_type'}>
                        <AppNameTitle />
                        <h1>{storeAccount ? 'Warehouse' : "Store Account"}</h1>
                    </div>
                </div>
            </div>
        </React.Fragment>
    );
};

export default Header;