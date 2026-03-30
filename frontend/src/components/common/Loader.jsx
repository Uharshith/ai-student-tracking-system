import "../../styles/global.css";

export default function Loader() {
  return (
    <div className="loader-wrapper">
      <div className="spinner"></div>
      <p className="loader-text">Loading...</p>
    </div>
  );
}