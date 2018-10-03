import React from 'react';
import '../css/loginform.css';
import '../css/vendor/bootstrap-4.0.0/bootstrap.min.css';
import './vendor/bootstrap-4.0.0/bootstrap.min.js'
import Greeting from './greeting';

class LoginForm extends React.Component {

    constructor(props) {
        super(props);
        // Remember! This binding is necessary to make `this` work in the callback
        this.loginHandler = this.loginHandler.bind(this);
        this.state = {
            formToDisplay: null,
            authenticated: false,
            password: '',
            username: '',
            oldPassword: '',
            newPassword: ''
        };
    }

    componentWillMount() {
        this.setState({authenticated: this.props.authMeta.authenticated}, this.setFormToDisplay(
            {auth: this.props.authMeta.authenticated}
        ))
    }

    componentWillUnmount() {

    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.authMeta.authenticated !== this.state.authenticated) {
            this.setState({authenticated: nextProps.authMeta.authenticated}, this.setFormToDisplay(
                {auth: nextProps.authMeta.authenticated}
            ))
        }
    }


    setFormToDisplay({form = null, auth = false} = {}) {
        if (auth) {
            this.setState({formToDisplay: form ? form : 'logout'})
        } else {
            this.setState({formToDisplay: 'login'})
        }
    }

    changePasswordFormDisplayHandler() {
        this.setFormToDisplay({form: 'changePassword', auth: this.state.authenticated})
    }

    loginHandler() {
        let username = this.state.username;
        let password = this.state.password;
        this.setState({username: '', password: ''});
        this.props.authenticate({
            apiTrigger: this.props.API_OPTIONS.POST_AUTH,
            requestData: {
                data: {
                    username: username,
                    password: password
                },
            }
        });
    }

    changePasswordHandler() {
        let oldPassword = this.state.oldPassword;
        let newPassword = this.state.newPassword;
        this.setState({oldPassword: '', newPassword: ''});
        this.props.authenticate({
            apiTrigger: this.props.API_OPTIONS.PATCH_CHANGE_PW,
            requestData: {
                data: {
                    old_password: oldPassword,
                    new_password: newPassword,
                    username: this.props.getSessionStorage('username')
                },
            },
            auth: this.state.authenticated
        });
    }

    handleLogout() {
        this.props.deleteSessionStorage(['apiToken', 'username']);
        this.props.authenticate({auth: false})
    }

    receivePassword(e) {
        this.setState({password: e.target.value})
    }

    receiveUsername(e) {
        this.setState({username: e.target.value})
    }

    receiveOldPassword(e) {
        this.setState({oldPassword: e.target.value})
    }

    receiveNewPassword(e) {
        this.setState({newPassword: e.target.value})
    }

    render() {
        let displayForm;
        switch (this.state.formToDisplay) {
            case 'login':
                displayForm = (
                    <form>
                        <div>
                            <div className="form-field">
                                <input className="form-control" placeholder="Username"
                                       value={this.state.username} onChange={(e) => this.receiveUsername(e)}/>
                            </div>
                            <div className="form-field">
                                <input className="form-control" placeholder="Password"
                                       type="password" value={this.state.password}
                                       onChange={(e) => this.receivePassword(e)}/>
                            </div>
                            <div className="form-field">
                                <button className="btn btn-primary"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            this.loginHandler()
                                        }}>Submit
                                </button>
                            </div>
                        </div>
                    </form>
                );
                break;
            case 'logout':
                displayForm = (
                    <div className="logout-button-field">
                        <span className="welcome">Welcome {this.props.getSessionStorage('username')}!</span>
                        <button className="btn btn-secondary"
                                onClick={() => this.changePasswordFormDisplayHandler()}>Change Password
                        </button>
                        <button className="btn btn-warning" onClick={() => this.handleLogout()}>Logout
                        </button>
                    </div>
                );
                break;
            case 'changePassword':
                displayForm = (
                    <form>
                        <div>
                            <div className="form-field">
                                <input className="form-control" id={'old_password'} value={this.state.oldPassword}
                                       type={'password'} placeholder="Old Password" onChange={(e) =>
                                    this.receiveOldPassword(e)}/>
                            </div>
                            <div className="form-field">
                                <input className="form-control" id={'new_password'} placeholder="New Password"
                                       type="password" value={this.state.newPassword} onChange={(e) =>
                                    this.receiveNewPassword(e)}/>
                            </div>
                            <div className="form-field">
                                <button className="btn btn-primary"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            this.changePasswordHandler()
                                        }}>Submit Change
                                </button>
                            </div>
                        </div>
                    </form>
                );
                break;
        }
        return (
            <div className={'container login'}>
                <div className={'row'}>
                    <div className={'col-4'}><Greeting greeting={this.props.greeting}/></div>
                    <div className={'col-8'}>{displayForm}</div>
                </div>
            </div>
        )
    }
}

export default LoginForm;