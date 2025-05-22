import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Component for the sidebar navigation
const Sidebar = ({ activeTab, setActiveTab }) => {
  return (
    <div className="w-64 bg-gray-800 text-white h-screen flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">CyberSec AI Bot</h1>
      </div>
      <nav className="flex-1 p-4">
        <ul>
          <li 
            className={`mb-2 p-2 rounded cursor-pointer ${activeTab === 'dashboard' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </li>
          <li 
            className={`mb-2 p-2 rounded cursor-pointer ${activeTab === 'dataset' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            onClick={() => setActiveTab('dataset')}
          >
            Dataset Management
          </li>
          <li 
            className={`mb-2 p-2 rounded cursor-pointer ${activeTab === 'search' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            onClick={() => setActiveTab('search')}
          >
            Search Engine
          </li>
          <li 
            className={`mb-2 p-2 rounded cursor-pointer ${activeTab === 'config' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
            onClick={() => setActiveTab('config')}
          >
            Configuration
          </li>
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-700">
        <p className="text-sm text-gray-400">CyberSec AI Assistant</p>
      </div>
    </div>
  );
};

// Dashboard component
const Dashboard = ({ status }) => {
  const [statusChecks, setStatusChecks] = useState([]);

  useEffect(() => {
    const fetchStatusChecks = async () => {
      try {
        const response = await axios.get(`${API}/status/checks`);
        setStatusChecks(response.data);
      } catch (error) {
        console.error("Error fetching status checks:", error);
      }
    };
    
    fetchStatusChecks();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className={`p-6 rounded-lg shadow-md ${status.app === 'running' ? 'bg-green-100' : 'bg-red-100'}`}>
          <h3 className="text-lg font-semibold mb-2">Application Status</h3>
          <p className={`text-sm ${status.app === 'running' ? 'text-green-600' : 'text-red-600'}`}>
            {status.app === 'running' ? 'Running' : 'Stopped'}
          </p>
        </div>
        
        <div className={`p-6 rounded-lg shadow-md ${status.telegram_bot === 'configured' ? 'bg-green-100' : 'bg-yellow-100'}`}>
          <h3 className="text-lg font-semibold mb-2">Telegram Bot</h3>
          <p className={`text-sm ${status.telegram_bot === 'configured' ? 'text-green-600' : 'text-yellow-600'}`}>
            {status.telegram_bot === 'configured' ? 'Configured' : 'Not Configured'}
          </p>
        </div>
        
        <div className={`p-6 rounded-lg shadow-md ${status.openai === 'configured' ? 'bg-green-100' : 'bg-yellow-100'}`}>
          <h3 className="text-lg font-semibold mb-2">OpenAI API</h3>
          <p className={`text-sm ${status.openai === 'configured' ? 'text-green-600' : 'text-yellow-600'}`}>
            {status.openai === 'configured' ? 'Configured' : 'Not Configured'}
          </p>
        </div>
        
        <div className={`p-6 rounded-lg shadow-md ${status.database === 'connected' ? 'bg-green-100' : 'bg-red-100'}`}>
          <h3 className="text-lg font-semibold mb-2">Database</h3>
          <p className={`text-sm ${status.database === 'connected' ? 'text-green-600' : 'text-red-600'}`}>
            {status.database === 'connected' ? 'Connected' : 'Disconnected'}
          </p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">Getting Started</h3>
        <p className="mb-4">Follow these steps to set up your Cybersecurity AI Assistant:</p>
        <ol className="list-decimal pl-6 space-y-2">
          <li>Configure your Telegram bot and OpenAI API keys in the Configuration tab</li>
          <li>Upload your cybersecurity datasets to train the AI</li>
          <li>Start using the Telegram bot to ask questions and search for information</li>
        </ol>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Recent System Checks</h3>
        {statusChecks.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b text-left">Client</th>
                  <th className="py-2 px-4 border-b text-left">Timestamp</th>
                  <th className="py-2 px-4 border-b text-left">ID</th>
                </tr>
              </thead>
              <tbody>
                {statusChecks.map((check, index) => (
                  <tr key={check.id}>
                    <td className="py-2 px-4 border-b">{check.client_name}</td>
                    <td className="py-2 px-4 border-b">{new Date(check.timestamp).toLocaleString()}</td>
                    <td className="py-2 px-4 border-b">{check.id.substring(0, 8)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No system checks recorded yet.</p>
        )}
      </div>
    </div>
  );
};

// Dataset Management component
const DatasetManagement = () => {
  const [datasets, setDatasets] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`);
      setDatasets(response.data);
    } catch (error) {
      console.error("Error fetching datasets:", error);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name || !description || !file) {
      setMessage({ text: "Please fill all fields and select a file", type: "error" });
      return;
    }
    
    setUploading(true);
    setMessage({ text: "", type: "" });
    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("file", file);
    
    try {
      await axios.post(`${API}/dataset/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      setName("");
      setDescription("");
      setFile(null);
      setMessage({ text: "Dataset uploaded successfully", type: "success" });
      
      // Refresh the dataset list
      fetchDatasets();
    } catch (error) {
      console.error("Error uploading dataset:", error);
      setMessage({ text: "Failed to upload dataset", type: "error" });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Dataset Management</h2>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">Upload New Dataset</h3>
        
        {message.text && (
          <div className={`p-4 mb-4 rounded ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
              Dataset Name
            </label>
            <input
              id="name"
              type="text"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="file">
              Dataset File
            </label>
            <input
              id="file"
              type="file"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              onChange={handleFileChange}
              required
            />
          </div>
          
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload Dataset"}
          </button>
        </form>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Uploaded Datasets</h3>
        
        {datasets.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b text-left">Name</th>
                  <th className="py-2 px-4 border-b text-left">Description</th>
                  <th className="py-2 px-4 border-b text-left">Upload Date</th>
                  <th className="py-2 px-4 border-b text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((dataset) => (
                  <tr key={dataset.id}>
                    <td className="py-2 px-4 border-b">{dataset.name}</td>
                    <td className="py-2 px-4 border-b">{dataset.description}</td>
                    <td className="py-2 px-4 border-b">{new Date(dataset.upload_date).toLocaleString()}</td>
                    <td className="py-2 px-4 border-b">
                      <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full 
                        ${dataset.status === 'complete' ? 'bg-green-100 text-green-800' : 
                          dataset.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          dataset.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                        {dataset.status.charAt(0).toUpperCase() + dataset.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No datasets uploaded yet.</p>
        )}
      </div>
    </div>
  );
};

// Search Engine component
const SearchEngine = () => {
  const [searchType, setSearchType] = useState("web");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query) return;
    
    setLoading(true);
    setResults([]);
    
    try {
      let response;
      
      if (searchType === "web") {
        response = await axios.post(`${API}/search/web`, { query });
        setResults(response.data.results);
      } else if (searchType === "person") {
        response = await axios.post(`${API}/search/person`, { name: query });
        setResults(response.data);
      }
      
      setSearched(true);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Search Engine</h2>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">Search</h3>
        
        <div className="mb-4">
          <div className="flex space-x-4">
            <div className="flex items-center">
              <input
                id="web-search"
                type="radio"
                name="search-type"
                value="web"
                checked={searchType === "web"}
                onChange={() => setSearchType("web")}
                className="mr-2"
              />
              <label htmlFor="web-search">Web Search</label>
            </div>
            
            <div className="flex items-center">
              <input
                id="person-search"
                type="radio"
                name="search-type"
                value="person"
                checked={searchType === "person"}
                onChange={() => setSearchType("person")}
                className="mr-2"
              />
              <label htmlFor="person-search">Person Search</label>
            </div>
          </div>
        </div>
        
        <form onSubmit={handleSearch} className="flex">
          <input
            type="text"
            className="flex-1 shadow appearance-none border rounded-l py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder={searchType === "web" ? "Enter search query..." : "Enter person name..."}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>
      
      {loading && (
        <div className="flex justify-center my-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {searched && !loading && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Search Results</h3>
          
          {searchType === "web" && (
            <>
              {results.length > 0 ? (
                <div className="space-y-4">
                  {results.map((result, index) => (
                    <div key={index} className="p-4 border rounded">
                      <h4 className="font-medium mb-1">
                        <a href={result.href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {result.title}
                        </a>
                      </h4>
                      <p className="text-sm text-gray-600 mb-1">{result.href}</p>
                      <p className="text-sm">{result.body}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No results found.</p>
              )}
            </>
          )}
          
          {searchType === "person" && (
            <>
              {results && results.name ? (
                <div>
                  <h4 className="font-medium mb-4">Information about {results.name}</h4>
                  
                  {results.social_profiles && results.social_profiles.length > 0 && (
                    <div className="mb-4">
                      <h5 className="font-medium mb-2">Social Profiles</h5>
                      <ul className="list-disc pl-5">
                        {results.social_profiles.map((profile, index) => (
                          <li key={index}>
                            <a href={profile.href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                              {profile.title}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {results.professional_info && results.professional_info.length > 0 && (
                    <div>
                      <h5 className="font-medium mb-2">Professional Information</h5>
                      <div className="space-y-2">
                        {results.professional_info.map((info, index) => (
                          <div key={index} className="p-2 border-b">
                            <p className="font-medium">{info.title}</p>
                            <p className="text-sm">{info.body}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p>No information found for this person.</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

// Configuration component
const Configuration = () => {
  const [telegramToken, setTelegramToken] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [telegramMessage, setTelegramMessage] = useState({ text: "", type: "" });
  const [openaiMessage, setOpenaiMessage] = useState({ text: "", type: "" });
  const [configuringTelegram, setConfiguringTelegram] = useState(false);
  const [configuringOpenai, setConfiguringOpenai] = useState(false);

  const configureTelegram = async (e) => {
    e.preventDefault();
    
    if (!telegramToken) {
      setTelegramMessage({ text: "Please enter a Telegram bot token", type: "error" });
      return;
    }
    
    setConfiguringTelegram(true);
    setTelegramMessage({ text: "", type: "" });
    
    try {
      const response = await axios.post(`${API}/config/telegram`, { token: telegramToken });
      
      if (response.data.status === "success") {
        setTelegramMessage({ text: response.data.message, type: "success" });
        setTelegramToken("");
      } else {
        setTelegramMessage({ text: response.data.message, type: "error" });
      }
    } catch (error) {
      console.error("Error configuring Telegram:", error);
      setTelegramMessage({ text: "Failed to configure Telegram bot", type: "error" });
    } finally {
      setConfiguringTelegram(false);
    }
  };

  const configureOpenai = async (e) => {
    e.preventDefault();
    
    if (!openaiKey) {
      setOpenaiMessage({ text: "Please enter an OpenAI API key", type: "error" });
      return;
    }
    
    setConfiguringOpenai(true);
    setOpenaiMessage({ text: "", type: "" });
    
    try {
      const response = await axios.post(`${API}/config/openai`, { api_key: openaiKey });
      
      if (response.data.status === "success") {
        setOpenaiMessage({ text: response.data.message, type: "success" });
        setOpenaiKey("");
      } else {
        setOpenaiMessage({ text: response.data.message, type: "error" });
      }
    } catch (error) {
      console.error("Error configuring OpenAI:", error);
      setOpenaiMessage({ text: "Failed to configure OpenAI API", type: "error" });
    } finally {
      setConfiguringOpenai(false);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Configuration</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Telegram Bot Configuration</h3>
          
          {telegramMessage.text && (
            <div className={`p-4 mb-4 rounded ${telegramMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {telegramMessage.text}
            </div>
          )}
          
          <form onSubmit={configureTelegram}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="telegram-token">
                Telegram Bot Token
              </label>
              <input
                id="telegram-token"
                type="text"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="Enter your Telegram bot token"
                value={telegramToken}
                onChange={(e) => setTelegramToken(e.target.value)}
              />
            </div>
            
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={configuringTelegram}
            >
              {configuringTelegram ? "Configuring..." : "Configure Telegram Bot"}
            </button>
          </form>
          
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <h4 className="font-medium mb-2">How to get a Telegram Bot Token:</h4>
            <ol className="list-decimal pl-4 text-sm">
              <li className="mb-1">Open Telegram and search for "@BotFather"</li>
              <li className="mb-1">Start a chat and send the command "/newbot"</li>
              <li className="mb-1">Follow the instructions to create a new bot</li>
              <li className="mb-1">BotFather will give you a token for your new bot</li>
              <li>Copy and paste that token here</li>
            </ol>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">OpenAI API Configuration</h3>
          
          {openaiMessage.text && (
            <div className={`p-4 mb-4 rounded ${openaiMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {openaiMessage.text}
            </div>
          )}
          
          <form onSubmit={configureOpenai}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="openai-key">
                OpenAI API Key
              </label>
              <input
                id="openai-key"
                type="text"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="Enter your OpenAI API key"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
              />
            </div>
            
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={configuringOpenai}
            >
              {configuringOpenai ? "Configuring..." : "Configure OpenAI API"}
            </button>
          </form>
          
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <h4 className="font-medium mb-2">How to get an OpenAI API Key:</h4>
            <ol className="list-decimal pl-4 text-sm">
              <li className="mb-1">Go to <a href="https://platform.openai.com/signup" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI's website</a> and create an account</li>
              <li className="mb-1">Navigate to the API section</li>
              <li className="mb-1">Go to "API Keys" and create a new secret key</li>
              <li>Copy and paste that key here</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App component
function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [status, setStatus] = useState({
    app: "unknown",
    telegram_bot: "unknown",
    openai: "unknown",
    database: "unknown"
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API}/status`);
        setStatus(response.data);
      } catch (error) {
        console.error("Error fetching status:", error);
      }
    };
    
    fetchStatus();
    
    // Refresh status every 30 seconds
    const intervalId = setInterval(fetchStatus, 30000);
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="flex bg-gray-100 min-h-screen">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === "dashboard" && <Dashboard status={status} />}
        {activeTab === "dataset" && <DatasetManagement />}
        {activeTab === "search" && <SearchEngine />}
        {activeTab === "config" && <Configuration />}
      </div>
    </div>
  );
}

export default App;
