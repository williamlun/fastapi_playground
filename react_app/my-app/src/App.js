import logo from './logo.svg';
import axios from "axios";
import './App.css';

function App() {

  function sayHello(msg) {
    console.log("hello world!")
    let url = "http://127.0.0.1:8077/authorize?redir_url=http://localhost:3000/"
    // axios.get("http://127.0.0.1:8077/authorize?redir_url=http://localhost:3000/")
    //   .then(res => { })
    fetch(url, { method: 'GET', redirect: 'follow' })
      .then(response => {
        response.redirect('/');
      })
      .catch(function (err) {
        console.info(err + " url: " + url);
      });
  }
  return (
    <div className="App">

      <button onClick={sayHello}> login</button >
    </div >
  );
}

export default App;
