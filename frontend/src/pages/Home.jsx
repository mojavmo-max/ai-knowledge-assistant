import {Link} from 'react-router-dom';

export default function Home(){
    return(
        <div>
            <h1>AI Assistant</h1>
            <Link to="/knowledge">
                Knowledge Assistant
            </Link>
            <Link to="/invoice">
                Invoice Assistant
            </Link>
        </div>
    );
}