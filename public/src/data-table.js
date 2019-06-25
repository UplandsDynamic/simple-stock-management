import React, { useState } from 'react';
import './css/data-table.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';
import moment from 'moment';
import 'moment/locale/en-gb.js';
import 'moment-timezone';
import DataTableNav from "./data-table-nav";
import DataTableData from "./data-table-data";
import DataTableHead from "./data-table-head";
import DataTableCaption from './data-table-caption';

const DataTable = ({ stockRecord = {}, setMessage, openStockUpdateModalHandler,
    getRecordsHandler, stockTakeHandler, authMeta = {}, setStockRecordState, accountModes, 
    accountMode, getStyles
} = {}) => {

    const [confirmAction, setConfirmAction] = useState(false);
    const { authenticated } = authMeta;

    const _formatUTCDateTime = ({ dateTime = null } = {}) => {
        // takes datetime in UTC, formats and returns datetime in user's browser reported timezone
        return dateTime ? `${moment.utc(dateTime).local()
            .format('DD/MM/YYYY HH:mm:ss')} ${moment.tz(moment.tz.guess()).zoneAbbr()}`
            : null;
    };

    const _handleColumnOrderChange = ({ stockRecord = {}, newOrder = {} } = {}) => {
        let { pageOrderDir, pageOrderBy } = stockRecord.meta;
        // set page order direction
        pageOrderDir = (!pageOrderBy || pageOrderDir === '-') ? '' : '-';  // *see note 1
        Object.assign(stockRecord.meta, { pageOrderBy: newOrder, pageOrderDir, page: 1 }); // maybe page:1 ?
        getRecordsHandler({ stockRecord })
    };

    const _handleAddRecord = ({ stockRecord = null } = {}) => {
        setMessage({ message: null });  // clear old messages
        openStockUpdateModalHandler({ stockRecord: stockRecord, newRecord: true }); // open modal
    };

    const _handleEditRecord = ({ stockRecord = null, deleteRecord = false } = {}) => {
        setMessage({ message: null }); // clear old messages
        openStockUpdateModalHandler({ stockRecord, deleteRecord });  // open update modal
    };

    const _handleStockTake = ({confirmed = false} = {}) => {
        setMessage({message: 'Initiating a stock take resets shrinkage & sales statistics ' + 
            'and generates a report. Are you sure you wish to continue?', 
            messageClass: 'alert alert-warning'
        })
        confirmed ? stockTakeHandler() : setConfirmAction(true);
    };

    const _handleSearch = ({ stockRecord = {}, term = null } = {}) => {
        if (stockRecord) {
            Object.assign(stockRecord.meta, {
                pageOrderBy: 'desc', page: 1,
                search: _validateDesc(term)
            });
            /* set new record state early, even though stockRecord again when API returns,
            to ensure search string change keeps pace with user typing speed
             */
            setStockRecordState({ newStockRecord: stockRecord });
            // get the matching records from the API
            getRecordsHandler({ stockRecord });
        }
    };

    const _validateDesc = (value) => {
        return (/^[a-zA-Z\d.\- ]*$/.test(value)) ? value : stockRecord.meta.search
    };

    const _handleConfirm = ({ cancel = true } = {}) => {
        !cancel ? _handleStockTake({ confirmed: true }) : setMessage(
            { message: 'Stock take cancelled', messageClass: 'alert alert-info' }
        );
        setConfirmAction(false);
    }

    const _stockTakeConfirmDialog = () => {
        return (
            <tr className={'d-flex dataTableRows'}>
                {authenticated ?
                    <td className={'col-12 text-center'}>
                        <button className={'btn btn-lg btn-warning mr-1'}
                            onClick={() => _handleConfirm({ cancel: false })}>Confirm Stock Take Initiation</button>
                        <button className={'btn btn-lg btn-secondary'} onClick={_handleConfirm}>
                            Cancel Stock Take</button>
                    </td> : <td className={'col-12'}></td>}
            </tr>
        );
    };

    return (
        <div className={'data-table'}>
            <DataTableNav
                stockRecord={stockRecord}
                handleGetRecords={getRecordsHandler}
                handleAddRecord={_handleAddRecord}
                handleStockTake={_handleStockTake}
                handleSearch={_handleSearch}
                authMeta={authMeta}
                accountMode={accountMode}
                accountModes={accountModes}
                getStyles={getStyles}
            />
            <div className={'container'}>
                <div className={'row'}>
                    <div className={'col-sm table-responsive table-sm'}>
                        <table className="table table-bordered table-dark table-hover">
                            <DataTableCaption
                                stockRecord={stockRecord}
                                accountMode={accountMode}
                                accountModes={accountModes}
                                formatUTCDateTime={_formatUTCDateTime}
                            />
                            <thead style={getStyles().recordTable}>
                                <DataTableHead
                                    stockRecord={stockRecord}
                                    handleColumnOrderChange={_handleColumnOrderChange}
                                    accountMode={accountMode}
                                    accountModes={accountModes}
                                />
                            </thead>
                            <tbody style={getStyles().recordTable}>
                                {!confirmAction ? <DataTableData
                                    stockRecord={stockRecord}
                                    formatUTCDateTime={_formatUTCDateTime}
                                    handleEditRecord={_handleEditRecord}
                                    authMeta={authMeta}
                                    accountMode={accountMode}
                                    accountModes={accountModes}
                                /> : _stockTakeConfirmDialog()}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    )
};

export default DataTable;
