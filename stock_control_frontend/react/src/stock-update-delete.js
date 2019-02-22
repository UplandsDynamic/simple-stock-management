import './css/data-table.css';
import React from 'react'

const StockUpdateDelete = ({stockRecord = null, handleCloseModal, handleRecordUpdate} = {}) => {
    const {desc, sku} = stockRecord.data.updateData;
    if (stockRecord.meta.deleteRecord) {
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className={'col-sm'}>
                            <h4>Delete "{desc}"</h4>
                            <form className={'form-control transfer-form-danger'}>
                                <label>Confirm deletion of "{desc}" (SKU: {sku})
                                    from the database:</label>
                                <div className={'btn-group-justified'}>
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