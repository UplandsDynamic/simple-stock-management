import React from 'react'
import '../css/greeting.css'
/*
Functional component to display the greeting (passed in as prop from loginform.jsx, set in state
in index.jsx).
 */
const Greeting = ({greeting = ''} = {}) => {
    return (
        <div className={'container'}>
            <div className={'row'}>
                <div className={'col-12'}>
                    {greeting}
                </div>
            </div>
        </div>
    );
};
export default Greeting;