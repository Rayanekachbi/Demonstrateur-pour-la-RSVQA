import React, { useEffect, useState } from "react";
import "./App.css"

import { useRef } from "react";

const Datasets = () => {
  // États pour la gestion des datasets
  const [datasets, setDatasets] = useState([]);
  const [hoveredDataset, setHoveredDataset] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [datasetImages, setDatasetImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const imagesPerPage = 12;
  const [validDatasetName, setValidDatasetName] = useState(null);


  // États pour la gestion des questions/réponses
  const [isQuestionCustom, setIsQuestionCustom] = useState(null);
  const [questionTypeSelected, setQuestionTypeSelected] = useState(false);
  const [displayedQuestions, setDisplayedQuestions] = useState([]);
  const [datasetAnswers, setDatasetAnswers] = useState({});
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [questionsError, setQuestionsError] = useState(null);
  const [modelResponses, setModelResponses] = useState({});
  const [loadingModelResponses, setLoadingModelResponses] = useState(false);
  const [modelResponsesError, setModelResponsesError] = useState(null);
  const [loadingDatasetAnswers, setLoadingDatasetAnswers] = useState(false);
  const [datasetAnswersError, setDatasetAnswersError] = useState(null);
  const [customQuestionText, setCustomQuestionText] = useState('');
  const [modelAnswer, setModelAnswer] = useState('');
  const [selectedModel, setSelectedModel] = useState('both');

  useEffect(() => {
    fetch("http://localhost:5000/datasets")
      .then((response) => response.json())
      .then((data) => setDatasets(data))
      .catch((error) =>
        console.error("Erreur lors du chargement des datasets:", error)
      );
  }, []);

   // Gestion de la sélection d'un dataset
  const handleMouseEnter = (dataset) => {
    setHoveredDataset(dataset);
  };

  const handleMouseLeave = () => {
    setHoveredDataset(null);
  };

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
    setIsLoading(true);
    setSelectedImage(null);
    setCurrentPage(1);
    setValidDatasetName(dataset.name); 
  
    fetch(`http://127.0.0.1:5000/api/get_all/${dataset.name}/images`)
      .then((response) => response.json())
      .then((data) => setDatasetImages(data.images))
      .catch((error) => {
        console.error("Erreur lors du chargement des images:", error);
        setDatasetImages([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };
  



// Focntion qui donne le nom de l'image ex: 1.tif
const getImageName = (url) => {
  if (!url) return '';
  const parts = url.split('/');
  return parts[parts.length - 1]; // "1.tif"
};

// Ajout d'une fonction pour extraire l'ID numérique
const extractImageId = (imageUrl) => {
  const imageName = getImageName(imageUrl); // "1.tif"
  return parseInt(imageName.split('.')[0], 10); // 1
};

  // Chargement des questions en fonction de l'image sélectionnée
  useEffect(() => {
    const fetchQuestions = async () => {
      if (selectedImage) {
        setLoadingQuestions(true);
        setQuestionsError(null);
        const imageName = selectedImage.split('/').pop();
        const imageId = parseInt(imageName.split('.')[0]);
        try {
          const response = await fetch(
            `http://localhost:5000/api/get_all/${validDatasetName}/all_questions`
          );
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          const data = await response.json();
          const filteredQuestions = data.questions.filter(
            (question) =>
              question.img_id === imageId &&
              (question.active === undefined || question.active === true)
          );          
          setDisplayedQuestions(filteredQuestions);
        } catch (error) {
          setQuestionsError('Erreur lors du chargement des questions.');
          setDisplayedQuestions([]);
        } finally {
          setLoadingQuestions(false);
        }
      } else {
        setDisplayedQuestions([]);
      }
    };
    fetchQuestions();
  }, [selectedImage, selectedDataset]);

  // Chargement des réponses du dataset
useEffect(() => {
    const loadDatasetAnswers = async () => {
      if (displayedQuestions.length > 0) {
        setLoadingDatasetAnswers(true);
        setDatasetAnswersError(null);
        const newDatasetAnswers = {};
        try {
          await Promise.all(displayedQuestions.map(async (question) => {
            const response = await fetch(
              `http://localhost:5000/get_answer/${validDatasetName}/all_answers?question_id=${question.id}`
            );            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            newDatasetAnswers[question.id] = data.answer;
          }));
          setDatasetAnswers(newDatasetAnswers);
        } catch (error) {
          setDatasetAnswersError('Erreur lors du chargement des réponses du dataset.');
          console.error("Erreur lors de la récupération des réponses du dataset:", error);
        } finally {
          setLoadingDatasetAnswers(false);
        }
      } else {
        setDatasetAnswers({});
      }
    };
    loadDatasetAnswers();
  }, [displayedQuestions]);

  // charge les réponses du modèle pour les questions prédéfinies
  useEffect(() => {
    const loadModelResponses = async () => {
      if (displayedQuestions.length > 0 && selectedImage) {
        setLoadingModelResponses(true);
        setModelResponsesError(null);
  
        const imageId = extractImageId(selectedImage);
        const questionsBatch = displayedQuestions.map(q => q.question);
  
        try {
          const response = await fetch('http://localhost:5000/ask_custom_question', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_id: imageId,
              questions: questionsBatch,
              dataset: validDatasetName,
            }),
          });
          console.log("Image envoyée :", selectedImage);
          console.log("Image ID :", imageId);
          console.log("Questions envoyées :", questionsBatch);
          console.log("Dataset :", validDatasetName);

          if (!response.ok) throw new Error('Erreur lors du chargement des réponses du modèle.');
          const data = await response.json();
          console.log("Réponse brute de l'API /ask_custom_question :", data);
          const newModelResponses = {};
          data.answers.forEach((item, idx) => {
            const questionId = displayedQuestions[idx].id;
            newModelResponses[questionId] = {
              answer_vqa: item.answer_vqa || "N/A",
              answer_vilt: item.answer_vilt || "N/A",
            };
          });
  
          setModelResponses(newModelResponses);
        } catch (error) {
          setModelResponsesError("Erreur lors du chargement des réponses du modèle.");
          console.error(error);
        } finally {
          setLoadingModelResponses(false);
        }
      } else {
        setModelResponses({});
      }
    };
    loadModelResponses();
  }, [displayedQuestions, selectedImage, validDatasetName]);
  

  // Gestion du type de question
  const handleQuestionTypeSelection = (event) => {
    setIsQuestionCustom(event.target.value === 'custom');
    setModelAnswer('');
    setCustomQuestionText('');
    setQuestionTypeSelected(true);
  };

  // Gestion de la question personnalisée
  const handleCustomQuestionInput = (event) => {
    setCustomQuestionText(event.target.value);
  };

  // Envoi de la question personnalisée au modèle
  const sendQuestionToModel = async () => {
    if (customQuestionText && selectedImage) {
      const imageName = selectedImage.split('/').pop();
      const imageId = extractImageId(selectedImage);

      try {
        const response = await fetch('http://localhost:5000/ask_custom_question', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: customQuestionText,
            image_id: imageId,
            dataset: validDatasetName
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          const errorMessage = errorData?.error || `HTTP error! status: ${response.status}`;
          setModelAnswer(`Erreur lors de la récupération de la réponse: ${errorMessage}`);
          console.error('Erreur lors de l\'envoi de la question:', errorMessage);
          return;
        }

        const data = await response.json();
        //Affichage des réponses selon le modèle choisi
        if (selectedModel === 'vqa') {
          setModelAnswer(data.answer_vqa || 'Pas de réponse VQA.');
        } else if (selectedModel === 'vilt') {
          setModelAnswer(data.answer_vilt || 'Pas de réponse ViLT.');
        } else {
          setModelAnswer(`VQA: ${data.answer_vqa || 'N/A'} | ViLT: ${data.answer_vilt || 'N/A'}`);
        }
      } catch (error) {
        setModelAnswer(`Erreur de connexion avec l'API: ${error.message}`);
        console.error('Erreur lors de la communication avec l\'API:', error);
      }
    } else if (!customQuestionText) {
      setModelAnswer('Veuillez entrer une question personnalisée.');
    } else {
      setModelAnswer('Veuillez sélectionner une image avant de poser une question.');
    }
  };

    //Permet de réinitialiser la partie questions/réponses quand on change d'image
    useEffect(() => {
      // Réinitialisation complète quand on change d’image
      setIsQuestionCustom(null);
      setQuestionTypeSelected(false);
      setCustomQuestionText('');
      setModelAnswer('');
      setDisplayedQuestions([]);
      setDatasetAnswers({});
      setModelResponses({});
    }, [selectedImage]);
  


  // Calcul des images à afficher
  const indexOfLastImage = currentPage * imagesPerPage;
  const indexOfFirstImage = indexOfLastImage - imagesPerPage;
  const currentImages = datasetImages.slice(indexOfFirstImage, indexOfLastImage);
  const totalPages = Math.ceil(datasetImages.length / imagesPerPage);

  const handleImageSelect = (imageName) => {
    setSelectedImage(`http://127.0.0.1:5000/api/images/${validDatasetName}/${imageName.replace("Images_LR/", "")}`);

  };  
  

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    document.getElementById('image-gallery-section').scrollIntoView({ behavior: 'smooth' });
  };

  const handleBackToDatasets = () => {
    setSelectedDataset(null);
    setDatasetImages([]);
    setSelectedImage(null);
    document.getElementById('datasets').scrollIntoView({ behavior: 'smooth' });
  };

  const activeDataset = hoveredDataset || selectedDataset;

  
  // Fonction pour gérer l'upload de dataset
  const handleDatasetUpload = (event) => {
    const files = event.target.files;
    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }
    fetch("http://127.0.0.1:5000/api/upload-dataset", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Dataset ajouté :", data);
        return fetch("http://localhost:5000/datasets")
          .then((response) => response.json())
          .then((data) => setDatasets(data));
      })
      .catch((err) => console.error("Erreur d’upload :", err));
  };

  return (
    <div id="datasets" className="datasets-section">
      <h2 className="neon-white">Datasets</h2>
      
      
      {!selectedDataset ? (
        <>
          <div className="dataset-container">
            
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className="dataset-card"
                onMouseEnter={() => handleMouseEnter(dataset)}
                onMouseLeave={handleMouseLeave}
                onClick={() => {
                  handleDatasetSelect(dataset);
                  setTimeout(() => {
                    document.getElementById('image-gallery-section').scrollIntoView({ behavior: 'smooth' });
                  }, 300);
                }}
              >
                <img
              src={`http://127.0.0.1:5000/api/images/${dataset.name}/${dataset.image.split("/").pop()}`}
              alt={dataset.name}
              className="dataset-image"
            />
                <p className="dataset-name">{dataset.name}</p>
              </div>
            ))}
            <input
              type="file"
              webkitdirectory="true"
              directory=""
              multiple
              onChange={handleDatasetUpload}
              style={{ display: "none" }}
              ref={fileInputRef}
              />
            <div className="dataset-card add-dataset"
                onClick={() => fileInputRef.current.click()}>
              <div className="add-icon">+</div>
              <p className="dataset-name">Ajouter un dataset</p>
            </div>
            <div className="circle-datasets-bg"></div>

          </div>
          
          <div className="dataset-info">
            {activeDataset ? (
              <div>
                <h2>{activeDataset.name}</h2>
                <p>
                  <strong>Propriétaire :</strong> {activeDataset.owner || "N/A"}
                </p>
                <p>
                  <strong>Nombre d'images :</strong>{" "}
                  {activeDataset.num_images || "N/A"}
                </p>
                <p>
                  <strong>Modes disponibles :</strong>{" "}
                  {activeDataset.modes || "N/A"}
                </p>
              </div>
            ) : (
              <ul >
                <li>Passez la souris sur un dataset pour voir les détails</li>
                <li>Cliquez pour afficher les images du dataset</li>
                <li>Cliquez sur "Ajouter un dataset" pour en importer un <br></br>(NB: doit contenir un dossier Images_LR ou serons stockés les images)</li>
              </ul >
            )}
          </div>
        </>
      ) : (
        <div className="back-button-container">
          <button onClick={handleBackToDatasets} className="back-button">
            &larr; Retour aux datasets
          </button>
        </div>
      )}

      <section id="image-gallery-section">
        {selectedDataset && (
          <div className="image-gallery-container">
            <h2>Images du  {validDatasetName}</h2>
            
            {isLoading ? (
              <div className="loading-spinner"></div>
            ) : (
              <>
                <div className="image-gallery">
                  <div className="image-grid">
                    {currentImages.map((imageName) => (
                      <img
                        key={imageName}
                        src={`http://127.0.0.1:5000/api/images/${validDatasetName}/${imageName.replace("Images_LR/", "")}`}
                        alt={imageName}
                        onClick={() => handleImageSelect(imageName)}
                        className="image-thumbnail"
                        loading="lazy"
                      />
                    ))}
                  </div>
                </div>

                {datasetImages.length > imagesPerPage && (
                  <div className="pagination">
                    <button 
                      onClick={() => paginate(currentPage - 1)} 
                      disabled={currentPage === 1}
                      className="page-btn"
                    >
                      Précédent
                    </button>
                    
                    {[...Array(totalPages).keys()].map(number => (
                      <button
                        key={number + 1}
                        onClick={() => paginate(number + 1)}
                        className={`page-btn ${currentPage === number + 1 ? 'active' : ''}`}
                      >
                        {number + 1}
                      </button>
                    ))}
                    
                    <button 
                      onClick={() => paginate(currentPage + 1)} 
                      disabled={currentPage === totalPages}
                      className="page-btn"
                    >
                      Suivant
                    </button>
                  </div>
                )}

                  {/* Image sélectionnée + Questions/Réponses */}
                  {selectedImage && (
                    <div className="qa-image-container">
                      <div className="circle-questions-bg2"></div>
                      <div className="circle-questions-bg"></div>
        
                      {/* Partie gauche : image */}
                      <div className="image-section">
                        <h3>Image sélectionnée :</h3>
                        <img src={selectedImage} alt="Sélectionnée" className="selected-image" />
                      </div>

                      {/* Partie droite : questions/réponses */}
                      <div className="qa-section">
                        <h2 className="neon-white">Questions & Réponses</h2>
                      {/* Section pour choisir le type de question */}
                    <div>
                      <label>
                        <input
                          type="radio"
                          value="predefined"
                          checked={isQuestionCustom === false} // Est coché si l'état 'isQuestionCustom' est false (ou initialement null)
                          onChange={handleQuestionTypeSelection} // Gère le changement de sélection
                        />
                        Question prédéfinie
                      </label>
                      <label>
                        <input
                          type="radio"
                          value="custom"
                          checked={isQuestionCustom === true} // Est coché si l'état 'isQuestionCustom' est true
                          onChange={handleQuestionTypeSelection} // Gère le changement de sélection
                        />
                        Question personnalisée
                      </label>
                    </div>

                    {/* Affiche le contenu en fonction du type de question sélectionné */}
                    {questionTypeSelected && (
                      <>
                        {/* Affiche le tableau des questions prédéfinies si 'isQuestionCustom' est false */}
                        {!isQuestionCustom && (
                          <div className="table-wrapper">
              
                            {loadingQuestions && <p>Chargement des questions...</p>}
                            {questionsError && <p className="error">{questionsError}</p>}
                            {(loadingDatasetAnswers || loadingModelResponses) && displayedQuestions.length > 0 && <p>Chargement des réponses...</p>}
                            {datasetAnswersError && <p className="error">{datasetAnswersError}</p>}
                            {modelResponsesError && <p className="error">{modelResponsesError}</p>}
                            {!loadingQuestions && !questionsError && displayedQuestions.length > 0 && (
                              <table>
                                <thead>
                                  <tr>
                                    <th>ID Question</th>
                                    <th>Question</th>
                                    <th>Réponse Dataset</th>
                                    <th>Réponse VQAModel</th>
                                    <th>Réponse ViLT</th> 
                                  </tr>
                                </thead>
                                <tbody>
                                  {displayedQuestions.map((question) => (
                                    <tr key={question.id}>
                                      <td>{question.id}</td>
                                      <td>{question.question}</td>
                                      {/* Réponse du Dataset */}
                                      <td>{datasetAnswers[question.id] || 'Chargement des réponses du dataset...'}</td>
                                      {/* Réponse VQAModel avec mise en gras si correcte par rapport au dataset */}
                                      <td style={{
                                        fontWeight: modelResponses[question.id]?.answer_vqa === datasetAnswers[question.id] ? 'bold' : 'normal'
                                      }}> 
                                      {modelResponses[question.id]?.answer_vqa || 'Chargement des réponses du modèle rsvqa...'}</td>
                                      {/* Réponse ViLT avec mise en gras si correcte par rapport au dataset*/}
                                      <td style={{
                                        fontWeight: modelResponses[question.id]?.answer_vilt === datasetAnswers[question.id] ? 'bold' : 'normal'
                                      }}>
                                      {modelResponses[question.id]?.answer_vilt || 'Chargement des réponses du modèle ViLT...'}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                            {!loadingQuestions && !questionsError && displayedQuestions.length === 0 && (
                              <p>Aucune question prédéfinie trouvée pour cette image.</p>
                            )}
                            <div className="circle-datasets-bg"></div>
                          </div>
                        )}

                        {/* Affiche le champ de texte et le bouton pour la question personnalisée si 'isQuestionCustom' est true */}
                        {isQuestionCustom && (
                          <>
                          {/* Menu déroulant pour choisir le modèle */}
                          <div className="model-selection">
                            <label>Choisissez le modèle :</label>
                              <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                                <option value="vqa">Modèle RSVQA</option>
                                <option value="vilt">Modèle ViLT</option>
                                <option value="both">Les deux modèles</option>
                              </select>
                          </div>
                          {/* Champ texte + bouton */}
                          <textarea
                            placeholder="Entrez votre question personnalisée ici"
                            value={customQuestionText}
                            onChange={handleCustomQuestionInput}
                            className="textarea"
                          />
                          <button
                            onClick={sendQuestionToModel}
                            disabled={!customQuestionText || !selectedImage}
                            className="submitButton"
                          >
                          Envoyer la question
                          </button>

                          {/* Réponse du modèle */}
                            {modelAnswer && (
                              <div>
                                <strong>Réponse du modèle :</strong> {modelAnswer}
                              </div>
                            )}                               
                          </>
                        )}
                      </>
                    )}
                    
                  </div>
                </div>
              )}
            </>
          )}
          <div className="circle-datasets-bg"></div>
        </div>
      )}
    </section>
  </div>
);
};
export default Datasets;
