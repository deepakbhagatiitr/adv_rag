import React from 'react';
import PropTypes from 'prop-types';
import { AiOutlineCloudUpload } from "react-icons/ai";

const UploadForm = ({ onFileUpload }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="flex items-center">
      <input
        type="file"
        onChange={handleFileChange}
        className="hidden"
        id="file-input"
      />
      <label
        htmlFor="file-input"
        className="flex items-center justify-center w-10 h-10 text-white bg-blue-600 rounded-lg cursor-pointer hover:bg-blue-700"
      >
        <AiOutlineCloudUpload className="text-xl" />
      </label>
    </div>
  );
};

UploadForm.propTypes = {
  onFileUpload: PropTypes.func.isRequired,
};

export default UploadForm;
