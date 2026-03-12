import { Header } from "./components/Header/Header";
import { MainPage } from "./components/MainPage/MainPage";
import './styles/grid.scss';

export const App = () => (
    <div className="app">
        <Header />
        <main>
            <MainPage />
        </main>
    </div>
)