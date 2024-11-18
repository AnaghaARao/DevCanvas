import React from "react";

const SpinnerLoader = () => {
  const [text, setText] = useState("");
  const [showImg, setShowImg] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setText("waited for 3 seconds");
    }, 3000);
  }, []);

  return <div>{showImg ? "loading..." : <h3>{text}</h3>}</div>;
};

export default SpinnerLoader;
