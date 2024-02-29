import MainStyle from './components/MainStyle';
import NavBar from './components/nav/NavBar';
import NotistackProvider from './components/NotistackProvider';
import ThemeLocalization from './components/ThemeLocalization';
import AppInstallProvider from './contexts/AppInstallContext';
import GameProvider from './contexts/GameContext';
import MetadataProvider from './contexts/MetadataContext';
import Router from './routes';
import ThemeProvider from './theme';

import { initializeBrotli } from './utils/convertList';

// ----------------------------------------------------------------------

function App() {

  initializeBrotli();

  return (
    <ThemeProvider>
      <ThemeLocalization>
        <MetadataProvider>
          <AppInstallProvider>
            <GameProvider>
              <NotistackProvider>
                <NavBar />
                <MainStyle>
                  <Router />
                </MainStyle>
              </NotistackProvider>
            </GameProvider>
          </AppInstallProvider>
        </MetadataProvider>
      </ThemeLocalization>
    </ThemeProvider>
  );
}

export default App;
