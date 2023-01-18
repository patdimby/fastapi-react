import React from "react";

const Dashboard = (props) => {
  console.log(props.host);
  window.location.replace(props.host);
  return <div></div>;
};

export default Dashboard;
