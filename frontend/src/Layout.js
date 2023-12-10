import React from 'react';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';

import App from './App';
import Home from './Home';
import SignUp from './signup';

function Layout() {
    return (
        <div className="app">
            <>
                <Router>
                    <Routes>
                        <Route exact path="/" element={<App />} />
                        <Route exact path="/home" element={<Home />} />
                        <Route exact path="/signup" element={<SignUp />} />
                    </Routes>
                </Router>
            </>
        </div>
    )
}

export default Layout;