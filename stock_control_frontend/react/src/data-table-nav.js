import './css/data-table.css';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import Paginate from './paginate.js';
import React from 'react'

const DataTableNav = ({
                          stockRecord = null, handleGetRecords, handleAddRecord, handleSearch, authMeta = null
                      } = {}) => {
    const {userIsAdmin} = authMeta;
    if (stockRecord) {
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row nav-row'}>
                        <div className={'btn-group'}>
                            <div className={'col-sm'}>
                                <button onClick={() => {
                                    Object.assign(stockRecord.meta, {page: 1});
                                    handleGetRecords({stockRecord})
                                }} className={'btn btn-warning'}>
                                    <FontAwesomeIcon icon={"sync-alt"}/></button>
                            </div>
                            <div className={userIsAdmin ? 'col-sm' : 'd-none'}>
                                <button onClick={() => handleAddRecord({stockRecord})}
                                        className={'btn btn-warning'}>
                                    <FontAwesomeIcon icon={"plus"}/></button>
                            </div>
                        </div>
                        <div className={'col-sm'}>
                            <nav className={'search-navigation'}>
                                <input value={stockRecord.meta.search} placeholder={'Search'}
                                       name={'search'} className={'form-control search'}
                                       onChange={(e) => handleSearch(stockRecord, e)}/>
                            </nav>
                        </div>
                        <div className={'col-sm'}>
                            <nav className="nav-pagination" aria-label="Table data pages">
                                <Paginate stockRecord={stockRecord}
                                          handleGetRecords={handleGetRecords}
                                />
                            </nav>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
    return null;
};

export default DataTableNav;