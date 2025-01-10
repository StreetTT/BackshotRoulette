import '../styles/globals.css'; // Import global styles
import '../styles/App.css'; // Additional styles if needed

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

export default MyApp;
