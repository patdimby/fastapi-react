import React from "react";


const Navbar = () =>{
    return (
        <div className="flex justify-between items-center h-20 px-4">
            <div>
                <h1>TITLE.</h1>
            </div>
            <ul className="flex">
                <li>Home</li>
                <li>Register</li>
            </ul>
        </div>
        
    );
}

export default Navbar;