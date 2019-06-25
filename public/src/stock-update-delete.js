import './css/data-table.css';
import React from 'react'

const StockUpdateDelete = ({ stockRecord = null, authMeta = null, handleCloseModal, handleRecordUpdate, deleteRecord = false, accountModes, accountMode } = {}) => {
    const { desc, sku, unit_price, units_total, selling_price } = stockRecord.data.updateData;
    const userIsAdmin = authMeta.userIsAdmin;
    const storeAccount = accountMode === accountModes.STORE;
    if (deleteRecord && !storeAccount) {
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className={'col-sm'}>
                            <form className={'form-control transfer-form-danger'}>
                                <h4>Delete "{desc}"?</h4>
                                <ul>
                                    <li>Description: {desc}</li>
                                    <li>SKU: {sku}</li>
                                    <li>Current Unit Price: {unit_price}</li>
                                    <li>Units In Stock: {units_total}</li>
                                </ul>
                                <label>Confirm permanent deletion of this stock line?</label>
                                <div className={'text-center'}>
                                    <div className={'btn-group-justified deleteButtons'}>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                return handleRecordUpdate({ adminUpdate:userIsAdmin , accountMode, accountModes, deleteRecord: true });
                                            }}
                                            className={'delete-btn btn btn-danger'}>Yes, delete!
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                return handleCloseModal({ actionCancelled: true });
                                            }}
                                            className={'cancel-btn btn btn-secondary'}>No, cancel!
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    } else if (deleteRecord && storeAccount) {
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className={'col-sm'}>
                            <form className={'form-control transfer-form-danger'}>
                                <h4>Delete "{desc}"?</h4>
                                <ul>
                                    <li>Description: {desc}</li>
                                    <li>SKU: {sku}</li>
                                    <li>Current Selling Price: {selling_price}</li>
                                    <li>Units In Stock: {units_total}</li>
                                </ul>
                                <label>Confirm permanent deletion of this stock line?</label>
                                <div className={'text-center'}>
                                    <div className={'btn-group-justified deleteButtons'}>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                return handleRecordUpdate({ adminUpdate: userIsAdmin, accountMode, accountModes, deleteRecord: true });
                                            }}
                                            className={'delete-btn btn btn-danger'}>Yes, delete!
                                </button>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                return handleCloseModal({ actionCancelled: true });
                                            }}
                                            className={'cancel-btn btn btn-secondary'}>No, cancel!
                                </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
    return null;
};
export default StockUpdateDelete;