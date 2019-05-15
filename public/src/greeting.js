import React from 'react'
import './css/greeting.css'
/*
Functional component to display the greeting (passed in as prop from loginform.js, set in state
in index.js).
 */
const Greeting = ({greeting = ''} = {}) => {
    return (
        <div className={'container'}>
            <div className={'row'}>
                <div className={'col-12'}>
                    <span>{greeting}</span>
                </div>
            </div>
        </div>
    );
};
export default Greeting;