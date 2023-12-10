import React, { useState } from "react";
import axios from "axios";
import "./Home.css";

function Home() {
  const [inpFile, setFile] = useState();
  const [validationMsg, setValidationMsg] = useState();
  const handleChange = (e) => {
    e.preventDefault();
    setFile(e.target.files[0]);
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationMsg("");
    const formData = new FormData();
    formData.append("inpFile", inpFile);
    const config = {
      headers: {
        "content-type": "multipart/form-data",
      },
    };
    axios
      .post("http://localhost:5000/api/upload/file/", formData, config)
      .then((response) => {
        console.log(response);
        const { message } = response.data;
        setValidationMsg(message);
      })
      .catch((err) => {
        console.log(err);
        const { data } = err.response.data;
        setValidationMsg(data);
      });
  };
  const userName = localStorage.getItem("userName");
  return (
    <div>
      <div className="logout">
        <input type="submit" value="Logout" />
      </div>
      <div className="main">
        <h1>Hello, {userName}</h1>
        <label htmlFor="myfile">Select a file:</label>
        <br />
        <input
          type="file"
          id="inpFile"
          name="inpFile"
          onChange={handleChange}
        />
        <br />
        <br />
        <br />
        <input type="submit" value="Submit" onClick={handleSubmit} />
        <br />
        <p>{validationMsg}</p>
      </div>
    </div>
  );
}

export default Home;
