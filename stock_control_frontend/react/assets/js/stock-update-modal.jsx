import React from 'react';
import '../css/stock-update-modal.css';
import Modal from "react-modal";
import Env from './env.jsx';

Modal.setAppElement('#react-app');

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
    maxWidth: '800px'
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
        // Remember! This binding is necessary to make `this` work in the callback
        // keep real-time props changes in component state
        this.state = {
            stockUpdateMeta: this.props.stockUpdateMeta,
            modalIsOpen: false,
            id: null,
            units_total: 0,
            unit_price: 0.00,
            desc: '',
            sku: '',
            unitsToTransfer: 0,
            newRecord: false,
            deleteRecord: false,
            modalStyles: {content: REGULAR_STYLES}
        };
        this.handleOpenModal = this.handleOpenModal.bind(this);
        this.handleAfterOpenModal = this.handleAfterOpenModal.bind(this);
        this.handleCloseModal = this.handleCloseModal.bind(this);
    }

    componentWillMount() {
    }

    componentWillUnmount() {
    }


    componentWillReceiveProps(nextProps) {
        this.setState({
            stockUpdateMeta: nextProps.stockUpdateMeta,
            id: nextProps.stockUpdateData.id,
            units_total: nextProps.stockUpdateData.units_total,
            unit_price: nextProps.stockUpdateData.unit_price,
            sku: nextProps.stockUpdateData.sku,
            desc: nextProps.stockUpdateData.desc,
            newRecord: nextProps.stockUpdateMeta.newRecord,
            deleteRecord: nextProps.stockUpdateMeta.deleteRecord
        });
        nextProps.stockUpdateMeta.deleteRecord ? this.state.modalStyles.content = DANGER_STYLES :
            this.state.modalStyles.content = REGULAR_STYLES;
        // if signal to open modal, open it
        if (nextProps.openStockUpdateModal) {
            this.handleOpenModal();
        }
    }

    handleOpenModal() {
        this.setState({modalIsOpen: true});
    }

    handleAfterOpenModal() {
       // this.subtitle.style.color = 'yellow';
    }

    handleCloseModal({actionCancelled = false} = {}) {
        // first clear temp values from component state
        this.setState({
            id: null,
            units_total: 0,
            unit_price: 0.00,
            sku: '',
            desc: '',
            unitsToTransfer: 0,
            stockUpdateMeta: null,
            newRecord: false,
            deleteRecord: false,
            modalIsOpen: false // close modal,
        });
        // set modal state in index.jsx back to closed
        this.props.setStockUpdateModalState({state: false, actionCancelled: actionCancelled});
    }

    handleRecordUpdate() {
        /*
        method to update record data (cancel if desc or sku fields were empty)
         */
        let allFieldsComplete = !!(this.state.desc && this.state.sku);
        if (allFieldsComplete) {
            this.props.setStockUpdateRecordState({
                record: {
                    data: {
                        units_total: this.state.units_total,
                        unit_price: this.state.unit_price,
                        sku: this.state.sku,
                        desc: this.state.desc
                    },
                    meta: {
                        url: `${Env().apiDataRoot}/stock/`
                    }
                },
                apiTrigger: this.state.newRecord ?
                    this.props.API_OPTIONS.ADD_STOCK : this.props.API_OPTIONS.PATCH_STOCK
            });
        }
        this.handleCloseModal({actionCancelled: !allFieldsComplete });
    }

    handleRecordDelete() {
        /*
        method to handle deletion of a stock line (record)
         */
        this.props.setStockUpdateRecordState({
            record: {
                meta: {
                    url: `${Env().apiDataRoot}/stock/${this.state.id}`
                }
            },
            apiTrigger: this.props.API_OPTIONS.DELETE_STOCK_LINE
        });
        this.handleCloseModal();
    }


    validatePrice(value) {
        return (/^[\d]*[\.]?[\d]{0,2}$/.test(value)) ? value : this.state.unit_price
    }

    validateDesc(value) {
        return (/^[a-zA-Z\d.\- ]*$/.test(value)) ? value : this.state.desc
    }

    generateEditForm() {
        if (this.state.stockUpdateMeta.deleteRecord) {
            return (
                <div className={'container'}>
                    <div className={'row'}>
                        <h4>Delete "{this.state.desc}"</h4>
                        <form className={'form-control transfer-form-danger'}>
                            <label>Confirm deletion of "{this.state.desc}" (SKU: {this.state.sku})
                                from the database:</label>
                            <div className={'btn-group-justified'}>
                                <button
                                    onClick={(e) => {
                                        this.handleRecordDelete();
                                    }}
                                    className={'delete-btn btn btn-danger'}>Yes, delete!
                                </button>
                                <button
                                    onClick={(e) => {
                                        this.handleCloseModal({actionCancelled: true});
                                    }}
                                    className={'cancel-btn btn btn-secondary'}>No, cancel!
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )
        } else if (this.state.stockUpdateMeta.userIsAdmin || this.state.stockUpdateMeta.newRecord) {
            // note: if newRecord, no userIsAdmin state has been set, hence need to test for newRecord separately
            return (
                <div className={'container'}>
                    <div className={'row'}>
                        <div className="col-sm">
                            <table className="table table-bordered table-dark table-hover">
                                <caption>Current Record</caption>
                                <thead>
                                <tr>
                                    <th scope={'col'}>Stock Attribute</th>
                                    <th scope={'col'}>Value</th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr>
                                    <th scope={'row'}><label>SKU</label></th>
                                    <td>
                                        <input value={this.state.sku}
                                               name={'sku'}
                                               onChange={e => this.setState({sku: e.target.value})}
                                               className={'form-control'} type={'text'}/>
                                    </td>
                                </tr>
                                <tr>
                                    <th scope={'row'}><label>Description</label></th>
                                    <td>
                                        <input value={this.state.desc}
                                               name={'description'}
                                               onChange={e => this.setState({desc: this.validateDesc(e.target.value)})}
                                               className={'form-control'} type={'text'}/>
                                    </td>
                                </tr>
                                <tr>
                                    <th scope={'row'}><label>Warehouse quantity</label></th>
                                    <td>
                                        <input value={this.state.units_total}
                                               name={'quantity'}
                                               onChange={e => this.setState({
                                                   units_total: e.target.value ? parseInt(e.target.value) : 0
                                               })}
                                               className={'form-control'} type={'number'}/>
                                    </td>
                                </tr>
                                <tr>
                                    <th scope={'row'}><label>Unit price</label></th>
                                    <td>
                                        <input value={this.state.unit_price}
                                               name={'unit-price'}
                                               onChange={e => this.setState({
                                                   unit_price:
                                                       this.validatePrice(e.target.value)
                                               })}
                                               className={'form-control'} type={'text'}
                                        />
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div className={'row'}>
                        <div className="col-sm">
                            <div className={'btn-group-justified'}>
                                <label>
                                    <button
                                        onClick={(e) => {
                                            e.preventDefault();
                                            this.handleRecordUpdate()
                                        }}
                                        className={'btn btn-warning'}>
                                        {this.state.newRecord ? 'New Stock Item' : 'Edit Stock Record'}
                                    </button>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
        else {
            return (
                <div className={'container'}>
                    <div className={'row'}>
                        <form className={'form-control transfer-form'}>
                            <label>
                                Units to transfer
                                <input value={this.state.unitsToTransfer}
                                       onChange={e =>
                                           this.setState({
                                               unitsToTransfer: e.target.value ? parseInt(e.target.value) : 0,
                                           })}  // updated display and actual value to be transferred
                                       className={'form-control'} type={'number'} min={'0'}/>
                            </label>
                            <div className={'btn-group-justified'}>
                                <label>
                                    <button
                                        onClick={(e) => {
                                            e.preventDefault();
                                            this.setState({units_total: this.state.units_total - this.state.unitsToTransfer}, () => {
                                                this.handleRecordUpdate();
                                            })
                                        }}
                                        className={'btn btn-warning'}>Transfer Stock
                                    </button>
                                </label>
                            </div>
                        </form>
                    </div>
                </div>
            )
        }
    }

    render() {
        if (this.state.stockUpdateMeta) {
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
                                {this.generateEditForm()}
                            </div>
                        </div>
                    </div>
                </Modal>
            );
        }
        else {
            return (
                <div></div>
            )
        }
    }
}

export default StockUpdateModal;