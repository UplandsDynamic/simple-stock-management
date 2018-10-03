import React from 'react';
import '../css/data-table.css';

class Message extends React.Component {

    constructor(props) {
        super(props);
        // keep real-time props changes in component state
        this.state = {
            message: null,
        };
    }

    componentWillMount() {
    }

    componentWillUnmount() {
    }

    componentWillReceiveProps(nextProps) {
        // generate new table
        this.setState({
            message: nextProps.message,
            messageClass: nextProps.messageClass,
        });
    }

    renderMessage = () => {
        let message = this.state.message ? this.state.message :
            this.state.datetimeOfRequest ? `Stock data queried ${this.state.datetimeOfRequest}` : '';
        let
            messageClass = this.state.messageClass ? this.state.messageClass : 'alert alert-info';
        return (
            <div className={'card message-card'}>
                <div className={'card-body'}>
                    <span className={'card-title'}></span>
                    <div className={`card-text ${messageClass}`}>
                        {message}
                    </div>
                </div>
            </div>
        )
    };

    render() {
        return (
            <div>
                {this.state.message ? this.renderMessage() : null}
            </div>
        )
    }
}

export default Message;