import boxLogo from './img/box.svg'
import './css/header.css';
import AppNameTitle from './app-name-title'
import LoginForm from './loginform'
import React from 'react'
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

const Header = ({
                    authMeta = {}, apiOptions = null, csrfToken = null, setMessage, getSessionStorage, setSessionStorage,
                    deleteSessionStorage, setAuthentication, openTruck
                } = {}) => {
    return (
        <React.Fragment>
            <div className={'container header'}>
                <div className={'row'}>
                    <div className={'col-4'}><img className={'logo float-left'} src={boxLogo}
                                                  alt={'Box logo'}/><AppNameTitle/></div>
                    <div className={'col-7'}><LoginForm authMeta={authMeta}
                                                        apiOptions={apiOptions}
                                                        csrfToken={csrfToken}
                                                        setMessage={setMessage}
                                                        getSessionStorage={getSessionStorage}
                                                        setSessionStorage={setSessionStorage}
                                                        deleteSessionStorage={deleteSessionStorage}
                                                        setAuthentication={setAuthentication}
                    /></div>
                    <div className={'col-1'}>
                        <button className={'float-right btn btn-lg btn-success'}
                                onClick={(e) => {
                                    e.preventDefault();
                                    openTruck({state: true})
                                }}><FontAwesomeIcon icon={"truck"}/>
                        </button>
                    </div>
                </div>
            </div>
        </React.Fragment>
    );
};

export default Header;