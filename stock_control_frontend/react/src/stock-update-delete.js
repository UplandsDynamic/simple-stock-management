import './css/data-table.css';
import React from 'react'

const StockUpdateDelete = ({stockRecord = null, handleCloseModal, handleRecordUpdate} = {}) => {
    const {desc, sku, unit_price, units_total} = stockRecord.data.updateData;
    if (stockRecord.meta.deleteRecord) {
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
                                                return handleRecordUpdate();
                                            }}
                                            className={'delete-btn btn btn-danger'}>Yes, delete!
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                return handleCloseModal({actionCancelled: true});
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