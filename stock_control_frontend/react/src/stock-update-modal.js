import React from 'react';
import './css/stock-update-modal.css';
import Modal from "react-modal";
import StockUpdateTable from './stock-update-table.js'
import StockUpdateDelete from './stock-update-delete.js'
import processRequest from './api.js'

Modal.setAppElement(document.body);

const REGULAR_STYLES = {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: '#001e00',
    color: 'yellow',
    border: '1px solid yellow',
    borderRadius: '7px 7px 7px 7px',
    boxShadow: '-7px -7px 17px 7px #001e00',
    maxWidth: '800px',
};

const DANGER_STYLES = {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: 'darkred',
    color: 'white',
    border: '1px solid yellow',
    borderRadius: '7px 7px 7px 7px',
    boxShadow: '-7px -7px 17px 7px #001e00',
    maxWidth: '800px'
};

class StockUpdateModal extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            modalStyles: {content: REGULAR_STYLES},
            modalIsOpen: this.props.openStockUpdateModal
        };
        // Remember! This binding is necessary to make `this` work in the callback
        this.handleAfterOpenModal = this.handleAfterOpenModal.bind(this);
        this.handleCloseModal = this.handleCloseModal.bind(this);
    }

    componentWillMount() {
    }

    componentWillUnmount() {
        console.log('Unmounting stock update modal')
    }

    componentWillReceiveProps(nextProps, nextContext) {
        nextProps.stockRecord.meta.deleteRecord ? this.setState({modalStyles: {content: DANGER_STYLES}}) :
            this.setState({modalStyles: {content: REGULAR_STYLES}});
        // set modal open/close state (source of truth in parent component - app.js)
        this.setState({modalIsOpen: nextProps.openStockUpdateModal});
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
    }

    handleAfterOpenModal() {
        // this.subtitle.style.color = 'yellow';
    }

    handleCloseModal({stockRecord = this.props.stockRecord, actionCancelled = false} = {}) {
        // set modal state in parent component (app,js) back to closed
        this.props.setStockUpdateModalState({stockRecord, state: false, actionCancelled: actionCancelled});
    }


    dataUpdate({stockRecord = this.props.stockRecord, updated = {}, commit = false} = {}) {
        if (commit) {
            this.handleCloseModal({stockRecord, actionCancelled: false}); // close modal (this makes new api request for updated data)
        } else {  // called from update modal table, so update just the updateData values, pending eventual api call
            Object.assign(stockRecord.data.updateData, {...updated});
            this.props.setStockRecordState({newStockRecord: stockRecord})
        }
    }

    handleRecordUpdate() {
        /*
        method to update or delete record data (cancel if desc or sku fields were empty)
         */
        const {desc, sku} = this.props.stockRecord.data.updateData;
        let reqFieldsComplete = !!((desc && sku) || this.props.stockRecord.meta.deleteRecord);  // these fields required to have a value
        // hit the api
        if (reqFieldsComplete) {
            const apiRequest = processRequest({
                stockRecord: this.props.stockRecord,
                apiMode: this.props.apiMode
            });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        if (response.status === 200) {
                            this.props.setMessage({
                                message: 'Records successfully updated!',
                                messageClass: 'alert alert-success'
                            });
                        } else if (response.status === 201) {
                            this.props.setMessage({
                                message: 'Records successfully added!',
                                messageClass: 'alert alert-success'
                            });
                        } else if (response.status === 204) {
                            this.props.setMessage({
                                message: 'Record deleted!',
                                messageClass: 'alert alert-success'
                            });
                        }
                    }
                    // update the main table with the new values
                    this.dataUpdate({updated: response.data, commit: true})
                }).catch(error => {
                    console.log(error);
                    this.props.setMessage({
                        message: 'An API error has occurred',
                        messageClass: 'alert alert-danger'
                    });
                    this.handleCloseModal({actionCancelled: !reqFieldsComplete}); // close modal
                });
            }
        }
    }

    render() {
        if (this.props.stockRecord) {
            return (
                <Modal
                    isOpen={this.state.modalIsOpen}
                    onAfterOpen={this.handleAfterOpenModal}
                    onRequestClose={this.handleCloseModal}
                    style={this.state.modalStyles}
                    contentLabel="Stock Action"
                >
                    <div className="container">
                        <div className="row">
                            <div className="col-sm">
                                <h2 ref={subtitle => this.subtitle = subtitle}>Manage Stock</h2>
                            </div>
                            <div className="col-sm close-modal-button-cell">
                                <button className="btn btn btn-outline-light close-button"
                                        onClick={() => {
                                            this.handleCloseModal({actionCancelled: true})
                                        }}>Cancel
                                </button>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm">
                                <StockUpdateDelete
                                    stockRecord={this.props.stockRecord}
                                    handleCloseModal={this.handleCloseModal.bind(this)}
                                    handleRecordUpdate={this.handleRecordUpdate.bind(this)}
                                />
                                <StockUpdateTable
                                    stockRecord={this.props.stockRecord}
                                    authMeta={this.props.authMeta}
                                    handleRecordUpdate={this.handleRecordUpdate.bind(this)}
                                    handleCloseModal={this.handleCloseModal.bind(this)}
                                    dataUpdate={this.dataUpdate.bind(this)}
                                />
                            </div>
                        </div>
                    </div>
                </Modal>
            );
        }
        return null;
    }
}

export default StockUpdateModal;