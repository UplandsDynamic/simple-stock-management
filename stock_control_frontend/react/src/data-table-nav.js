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
                        <div className={'col-12'}>
                            <div className={'btn-group float-right'}>
                                <nav className="nav-pagination float-right" aria-label="Table data pages">
                                    <Paginate stockRecord={stockRecord}
                                              handleGetRecords={handleGetRecords}
                                    />
                                </nav>
                            </div>
                        </div>
                    </div>
                    <div className={'row nav-row'}>
                        <div className={`${userIsAdmin ? 'col-2' : 'col-1'}`}>
                            <div className={'btn-group'}>
                                <button onClick={() => {
                                    Object.assign(stockRecord.meta, {page: 1});
                                    handleGetRecords({stockRecord})
                                }} className={'btn btn-md btn-warning mr-1 '}>
                                    <FontAwesomeIcon icon={"sync-alt"}/></button>
                                <button onClick={() => handleAddRecord({stockRecord})}
                                        className={`btn btn-md btn-warning mr-1 ${userIsAdmin ? '' : 'd-none'}`}>
                                    <FontAwesomeIcon icon={"plus"}/></button>
                            </div>
                        </div>
                        <div className={`${userIsAdmin ? 'col-10' : 'col-11'}`}>
                            <nav className={'search-navigation w-100 d-block ml-1'}>
                                <input value={stockRecord.meta.search} placeholder={'Search'}
                                       name={'search'} className={'form-control search'}
                                       onChange={(e) =>
                                           handleSearch({stockRecord, term: e.target.value})
                                       }/>
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