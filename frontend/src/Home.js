// src/Home.js
import React from "react";

const Home = ({ onScrollToImages}) => {
  return (
    <div id = "homepage" className="homepage">
      <div className="background-circle"></div>
      <div className="intro">
        <h1>RSVQA</h1>
        <h2>Remote Sensing Visual Question Answering</h2>
        <p>
        Remote Sensing Visual Question Answering (RSVQA) is a research field that combines remote sensing and artificial intelligence, specifically in the context of visual and linguistic understanding. The goal of RSVQA is to enable a model to analyze remote sensing images (such as satellite or aerial images) and answer natural language questions about them. These questions can cover various aspects, such as object detection, quantity estimation, terrain type identification, or spatial relationship analysis.
By integrating visual modalities (such as RGB, multispectral, or radar data) and textual information, RSVQA provides a powerful approach to extracting complex information from remote sensing images. This has applications in fields such as urban planning, natural resource management, and environmental monitoring.

        </p>
      </div>
    </div>
  );
};

export default Home; 
