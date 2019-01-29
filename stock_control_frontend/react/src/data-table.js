import React from 'react';
import Paginate from './paginate.js';
import './css/data-table.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import moment from 'moment'
import 'moment/locale/en-gb.js'
import 'moment-timezone'

class DataTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            modalIsOpen: false,
            dataTable: null,
            message: null,
            messageClass: '',
            datetimeOfRequest: null,
            search: ''
        };
    }

    static formatUTCDateTime({dateTime = null} = {}) {
        // takes datetime in UTC, formats and returns datetime in user's browser reported timezone
        return dateTime ? `${moment.utc(dateTime).local()
                .format('DD/MM/YYYY HH:mm:ss')} ${moment.tz(moment.tz.guess()).zoneAbbr()}`
            : null;
    }

    componentWillMount() {
        // kick it off, make a request for stock data ...
        this.handleGetRecords({stockRecord: {meta: this.props.stockRecordMeta}});
    }

    componentWillUnmount() {
    }

    componentWillReceiveProps(nextProps) {
        // generate new table
        this.setState({
            message: nextProps.message,
            messageClass: nextProps.messageClass,
            datetimeOfRequest: DataTable.formatUTCDateTime(
                {dateTime: nextProps.stockRecordMeta.datetime_of_request}),
            search: nextProps.stockRecordMeta.search,
            dataTable:
                this.generateTable({
                    stockRecordData: nextProps.stockRecordData,
                    stockRecordMeta: nextProps.stockRecordMeta
                }),
        });
    }

    handleGetRecords({stockRecord = {}} = {}) {
        this.props.setMessage({message: null});  // clear old messages
        this.props.setStockRecordState({
            stockRecord: stockRecord,
            apiTrigger: this.props.API_OPTIONS.GET_STOCK
        });  // set record request state
    }

    handleAddRecord() {
        this.props.setMessage({message: null});  // clear old messages
        this.props.openStockUpdateModalHandler({record: {meta: {newRecord: true}}}); // open modal
    }

    handleEditRecord({record = null} = {}) {
        this.props.setMessage({message: null}); // clear old messages
        this.props.openStockUpdateModalHandler({record: record});  // open update modal
    }

    handleDeleteLine({record = null} = {}) {
        this.props.setMessage({message: null}); // clear old messages
        this.props.openStockUpdateModalHandler({record: {data: record, meta: {deleteRecord: true}}})
    }

    handleSearch(e) {
        this.handleGetRecords({
            stockRecord: {
                meta: {
                    orderBy: 'desc', page: 1,
                    search: this.validateDesc(e.target.value)
                }
            }
        });
    }

    validateDesc(value) {
        return (/^[a-zA-Z\d.\- ]*$/.test(value)) ? value : this.state.search
    }

    generateTable({stockRecordData = {}, stockRecordMeta = {}} = {}) {
        let navBar = () => {
            return (<div className={'container'}>
                    <div className={'row nav-row'}>
                        <div className={'btn-group'}>
                            <div className={'col-sm'}>
                                <button onClick={() => this.handleGetRecords({
                                    stockRecord: {meta: {page: 1, preserveOrder: true}}
                                })
                                } className={'btn btn-warning'}>
                                    <FontAwesomeIcon icon={"sync-alt"}/></button>
                            </div>
                            <div className={stockRecordMeta.userIsAdmin ? 'col-sm' : 'd-none'}>
                                <button onClick={() => this.handleAddRecord()}
                                        className={'btn btn-warning'}>
                                    <FontAwesomeIcon icon={"plus"}/></button>
                            </div>
                        </div>
                        <div className={'col-sm'}>
                            <nav className={'search-navigation'}>
                                <input value={this.state.search} placeholder={'Search'}
                                       name={'search'} className={'form-control'}
                                       onChange={(e) => this.handleSearch(e)}/>
                            </nav>
                        </div>
                        <div className={'col-sm'}>
                            <nav className="nav-pagination" aria-label="Table data pages">
                                <Paginate records={{data: stockRecordData, meta: stockRecordMeta}}
                                          handleGetRecords={this.handleGetRecords.bind(this)}
                                />
                            </nav>
                        </div>
                    </div>
                </div>
            )
        };
        let noData = () => {
            return (
                <React.Fragment>
                    {navBar()}
                    <div className={'alert alert-warning'}> Loading data ...</div>
                </React.Fragment>
            );
        };
        let resultData = ({stockData = null} = {}) => {
            return stockData.data.results.length ?
                stockData.data.results.map((item) => {
                    return (<tr key={item.id} data-toggle="modal" className={'d-flex'}>
                        {/*<th scope="row">{item.id}</th>*/}
                        <td className={'col-2'}>{item.sku}</td>
                        <td className={'col-3'}>{item.desc}</td>
                        <td className={'col-1'}>{item.units_total}</td>
                        <td className={'col-2'}>{item.unit_price}</td>
                        <td className={'table-small-font col-2'}>
                            {DataTable.formatUTCDateTime({dateTime: item.record_updated})}</td>
                        <td className={'action-col col-2 '}>
                            <button onClick={() => this.handleEditRecord({record: {data: item}})}
                                    className={'table-btn btn btn-primary'}>
                                <FontAwesomeIcon icon={"edit"}/></button>
                            {stockRecordMeta.userIsAdmin ?
                                <button onClick={() => this.handleDeleteLine({record: item})}
                                        className={'table-btn btn btn-danger'}>
                                    <FontAwesomeIcon icon={"trash-alt"}/></button> : ''}
                        </td>
                    </tr>)
                }) : null;
        };
        let table = () => {
            let data = resultData({stockData: stockRecordData});
            return data ? (
                <React.Fragment>
                    {navBar()}
                    <div className={'container'}>
                        <div className={'row'}>
                            <div className={'col-sm table-responsive table-sm'}>
                                <table className="table table-bordered table-dark table-hover">
                                    <caption>{process.env.REACT_APP_SHORT_ORG_NAME} Stock
                                        Data {stockRecordMeta.datetime_of_request ?
                                            `[Request returned: ${this.state.datetimeOfRequest}]` : ''}
                                    </caption>
                                    <thead>
                                    <tr className={'d-flex'}>
                                        <th className={'col-2'} scope={'col'} onClick={() => this.handleGetRecords({
                                            stockRecord: {meta: {orderBy: 'sku', page: 1}}
                                        })}>
                                            SKU
                                        </th>
                                        <th className={'col-3'} scope={'col'} onClick={() => this.handleGetRecords({
                                            stockRecord: {meta: {orderBy: 'desc', page: 1}}
                                        })}>
                                            Description
                                        </th>
                                        <th className={'col-1'} scope={'col'} onClick={() => this.handleGetRecords({
                                            stockRecord: {meta: {orderBy: 'units_total', page: 1}}
                                        })}>
                                            Units
                                        </th>
                                        <th className={'col-2'} scope={'col'} onClick={() => this.handleGetRecords({
                                            stockRecord: {meta: {orderBy: 'unit_price', page: 1}}
                                        })}>
                                            Unit Price
                                        </th>
                                        <th className={'col-2'} scope={'col'} onClick={() => this.handleGetRecords({
                                            stockRecord: {meta: {orderBy: 'record_updated', page: 1}}
                                        })}>
                                            Record Updated
                                        </th>
                                        <th className={'col-2 action-col'} scope={'col'}>
                                            Action
                                        </th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {data}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </React.Fragment>
            ) : null;
        };
        return table() ? table() : noData();
    }

    render() {
        return (
            <div className={'data-table'}>
                {this.state.dataTable}
            </div>
        )
    }
}

export default DataTable;