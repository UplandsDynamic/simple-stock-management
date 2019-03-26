import React from 'react';
import './css/data-table.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js'
import moment from 'moment'
import 'moment/locale/en-gb.js'
import 'moment-timezone'
import DataTableNav from "./data-table-nav";
import DataTableData from "./data-table-data";
import DataTableHead from "./data-table-head";

const DataTable = ({
                       stockRecord = {}, apiOptions = {}, setMessage, openStockUpdateModalHandler,
                       getRecordsHandler, authMeta = {}, setStockRecordState,
                   } = {}) => {

    const _formatUTCDateTime = ({dateTime = null} = {}) => {
        // takes datetime in UTC, formats and returns datetime in user's browser reported timezone
        return dateTime ? `${moment.utc(dateTime).local()
                .format('DD/MM/YYYY HH:mm:ss')} ${moment.tz(moment.tz.guess()).zoneAbbr()}`
            : null;
    };

    const _handleColumnOrderChange = ({stockRecord = {}, newOrder = {}} = {}) => {
        let {pageOrderDir, pageOrderBy} = stockRecord.meta;
        // set page order direction
        pageOrderDir = (!pageOrderBy || pageOrderDir === '-') ? '' : '-';  // *see note 1
        Object.assign(stockRecord.meta, {pageOrderBy: newOrder, pageOrderDir, page: 1}); // maybe page:1 ?
        getRecordsHandler({stockRecord})
    };

    const _handleAddRecord = ({stockRecord = null} = {}) => {
        setMessage({message: null});  // clear old messages
        openStockUpdateModalHandler({stockRecord: stockRecord, newRecord: true}); // open modal
    };

    const _handleEditRecord = ({stockRecord = null, deleteRecord = false} = {}) => {
        setMessage({message: null}); // clear old messages
        openStockUpdateModalHandler({stockRecord, deleteRecord});  // open update modal
    };

    const _handleSearch = ({stockRecord = {}, term = null} = {}) => {
        if (stockRecord) {
            Object.assign(stockRecord.meta, {
                pageOrderBy: 'desc', page: 1,
                search: _validateDesc(term)
            });
            /* set new record state early, even though stockRecord again when API returns,
            to ensure search string change keeps pace with user typing speed
             */
            setStockRecordState({newStockRecord: stockRecord});
            // get the matching records from the API
            getRecordsHandler({stockRecord});
        }
    };

    const _validateDesc = (value) => {
        return (/^[a-zA-Z\d.\- ]*$/.test(value)) ? value : stockRecord.meta.search
    };

    return (
        <div className={'data-table'}>
            <DataTableNav
                stockRecord={stockRecord}
                handleGetRecords={getRecordsHandler}
                handleAddRecord={_handleAddRecord}
                handleSearch={_handleSearch}
                authMeta={authMeta}
            />
            <div className={'container'}>
                <div className={'row'}>
                    <div className={'col-sm table-responsive table-sm'}>
                        <table className="table table-bordered table-dark table-hover">
                            <caption>{process.env.REACT_APP_SHORT_ORG_NAME} Stock
                                Data {stockRecord.meta.datetime_of_request ?
                                    `[Request returned:
                                        ${_formatUTCDateTime({
                                        dateTime: stockRecord.meta.datetime_of_request
                                    })}]` : ''}
                            </caption>
                            <thead>
                            <DataTableHead
                                stockRecord={stockRecord}
                                handleColumnOrderChange={_handleColumnOrderChange}
                            />
                            </thead>
                            <tbody>
                            <DataTableData
                                stockRecord={stockRecord}
                                formatUTCDateTime={_formatUTCDateTime}
                                handleEditRecord={_handleEditRecord}
                                authMeta={authMeta}
                            />
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    )
};

export default DataTable;
