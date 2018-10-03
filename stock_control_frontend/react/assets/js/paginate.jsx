import React from "react";
import '../css/paginate.css'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'

class Paginate extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            records: {},
            totalPages: 0,
            currentPage: 1
        }
    }

    componentWillMount() {
        this.setState({
            records: this.props.records,
            totalPages: Math.ceil(this.props.records.data.data.count / this.props.records.meta.limit),
            currentPage: this.props.records.meta.page
        });
    }

    componentWillUnmount() {
    }

    componentWillReceiveProps(nextProps) {
        let count = nextProps.records.data.data.count || 0;
        this.setState({
            records: nextProps.records,
            totalPages: Math.ceil(count / nextProps.records.meta.limit),
            currentPage: nextProps.records.meta.page
        });
    }

    validatePage(value) {
        // if input is a number or space (allowing for backspace), return value (if 0 change to 1), else current page
        return /^[\d\s]*$/.test(value) ? parseInt(value) === 0 ? 1 : value : this.state.currentPage;
    }

    switchPage = ({linkedPage = 0, dir = 'selected'} = {}) => {
        let page, url = null;
        switch (dir) {
            case 'selected':
                page = linkedPage;
                break;
            case 'previous':
                page = this.state.records.meta.page >= 1 ? this.state.records.meta.page - 1 : 1;
                url = this.state.records.data.data.previous;
                break;
            case 'next':
                page = this.state.totalPages > this.state.records.meta.page ?
                    this.state.records.meta.page + 1 : this.state.records.meta.page;
                url = this.state.records.data.data.next;
                break;
        }
        this.props.handleGetRecords({stockRecord: {meta: {page: page, url: url, preserveOrder: true}}})
    };

    currentPage = () => {
        return (
            <React.Fragment>
                <div className={'linkedPage'}>
                    <label>Page </label>
                    <input onKeyDown={(e) => e.keyCode === 8 ? this.setState({currentPage: ''}) : null}
                           onChange={(e) => {
                               this.switchPage({
                                   linkedPage: parseInt(e.target.value) > 0 ? parseInt(e.target.value)
                                   <= this.state.totalPages ? parseInt(e.target.value) : this.state.totalPages : 1,
                                   dir: 'selected'
                               });
                           }} value={this.state.currentPage} type={'text'}
                           className={'form-control input-sm page-input'}/>
                </div>
            </React.Fragment>
        );
    };

    prevSection = () => {
        return (
            <React.Fragment>
                <li className="page-item"><a href="#" aria-label="previous" onClick={
                    () => this.switchPage({dir: 'previous'})} className="page-link"><span
                    aria-hidden="true">&laquo;</span>
                    <span className="sr-only">Previous</span></a></li>
            </React.Fragment>
        )
    };

    nextSection = () => {
        return (
            <React.Fragment>
                <li className="page-item"><a aria-label="next" onClick={
                    () => this.switchPage({dir: 'next'})} href="#" className="page-link"><span
                    aria-hidden="true">&raquo;</span>
                    <span className="sr-only">Next</span></a></li>
            </React.Fragment>
        )
    };

    mainSection = () => {
        let pageItemClass;
        let pagerMainSize = this.state.records.meta.pagerMainSize;
        let linkedPage = this.state.records.meta.page;
        let totalPages = isNaN(this.state.totalPages) ? 0 : this.state.totalPages;
        return (
            <React.Fragment>
                {[...Array(totalPages)].map((o, pageIndex) => {
                    /* if selected (displayed) page is this list item, add 'active' to class to colour it
                    and remove elements over the max size of displayed list */
                    pageIndex + 1 > pagerMainSize ? pageItemClass = 'd-none' :
                        linkedPage === (pageIndex + 1) ? pageItemClass = 'active page-item' :
                            pageItemClass = 'page-item';
                    return (<li className={pageItemClass} key={pageIndex + 1}>
                        <a href="#" onClick={() => this.switchPage({linkedPage: pageIndex + 1, dir: 'selected'})}
                           className="page-link">
                            {pageIndex + 1}
                        </a>
                    </li>);
                })}
            </React.Fragment>
        );
    };

    endSection = () => {
        let pagerMainSize = this.state.records.meta.pagerMainSize;
        let linkedPage = this.state.records.meta.page;
        let totalPages = this.state.totalPages;
        let numEndEle = this.state.records.meta.pagerEndSize;
        let iterArray = Array.apply(null, {length: numEndEle}); // create array as basis for map in frag to iterate
        return (
            <React.Fragment>
                {iterArray.map((o, c) => {
                    let p = (iterArray.length - (c + 1));  // flip count order
                    let page = (totalPages - p) || 0;
                    return (
                        <li key={p}
                            className={page > pagerMainSize ? linkedPage === page ? 'active page-item' : 'page-item' : 'd-none'}>
                            <a onClick={() => this.switchPage({linkedPage: page, dir: 'selected'})} href="#"
                               className="page-link">{page}</a></li>)
                })}
            </React.Fragment>
        );
    };

    render() {
        return (<div className={'pager'}>
                {this.currentPage()}
                <ul className={'pagination pagination-sm'}>
                    {this.prevSection()}
                    {this.mainSection()}
                    <span className={'splitter'}>
                <FontAwesomeIcon icon={"ellipsis-h"}/></span>
                    {this.endSection()}
                    {this.nextSection()}
                </ul>
            </div>
        );
    }
}

export default Paginate;