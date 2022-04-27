import "../styles/globals.css";
import Navbar from "../components/Navbar";
import { config } from '@fortawesome/fontawesome-svg-core'
import '@fortawesome/fontawesome-svg-core/styles.css'
config.autoAddCss = false


function MyApp({ Component, pageProps }) {
  const links = [{
    "title": "Strategies",
    "address": "./Strategies"
  }
]
  return (
    <div className="bg-neutral-800 h-fit min-h-screen">
      <Navbar primaryColor={'bg-neutral-800'} secondaryColor={'hover:bg-neutral-600'} variant={'light'} title={'Algorithmic Trading'} links={links} />
      <Component {...pageProps} />
    </div>
  );
}

export default MyApp;
