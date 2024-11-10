import { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

function App() {
    // enkrip
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState('');
  const [resultImageUrl, setResultImageUrl] = useState('');
  const [encryptionKey, setEncryptionKey] = useState('');
  const [pilihan, setPilihan] = useState('');

  // dekrip
  const [images, setImages] = useState(null)
  const [key, setKey] = useState('')
  const [decryptedMessage, setDecryptedMessage] = useState('');


  // Konfigurasi untuk dropzone
  const onDrop = (acceptedFiles) => {
    // Mengambil file pertama yang di-drop
    const selectedFile = acceptedFiles[0];
    setImage(selectedFile);
    setImages(selectedFile)
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: 'image/*',
    multiple: false,
  });

  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };

  const handlePilihan = (e) => {
    setPilihan(e.target.value)
  }

  const handleKeyChange = (e) => {
    setKey(e.target.value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('image', image);
    formData.append('pesan', message);

    try {
      const response = await axios.post('http://127.0.0.1:5000/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResultImageUrl(response.data.path);
      setEncryptionKey(response.data.key);

      setImage(null)
      setMessage('')
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleSubmitDekrip = async (e) => {
    e.preventDefault()

    if (!images || !key) {
        return 'Please provide both a file and a key!';
    }

    const formData = new FormData();
    formData.append('images', images);
    formData.append('key', key);

    try {
        const response = await fetch('http://127.0.0.1:5000/dekrip', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to decrypt message');
        }
        const result = await response.json();
        setDecryptedMessage(result.pesan);

        setImage(null)
        setKey('')
    } catch (error) {
        return 'Error decrypting file: ' + error.message
    }

  }

  return (
    <div className='h-screen bg-gray-500 flex'>
      <div className="pilihan mr-5 mt-1">
          <select name="pilihan" id="pilihan" className='py-3' value={pilihan} onChange={handlePilihan}>
            <option value="encryption">Encryption</option>
            <option value="decription">Decryption</option>
          </select>
        </div>
      {pilihan === 'decription' ? (
        <>
          <form onSubmit={handleSubmitDekrip} className='w-[50%] flex flex-col justify-center items-center h-screen'>
            <div className='w-[auto]flex justify-center'>
            <div className='w-[auto]flex justify-center'>
            {image ? (
              <img src={URL.createObjectURL(image)} className='p-5' />
            ) : (
            <div {...getRootProps()} className='border-2 p-10 rounded-md cursor-pointer'>
              <input {...getInputProps()} />

              {isDragActive ? (
                <p>Drop the image here...</p>
              ) : (
                <p>Drag & drop an image here, or click to select a file</p>
              )}
            </div>

            )}
            </div>
            </div>
            <input type="text" name='key' value={key} onChange={handleKeyChange} autoComplete='off' />
            <button type="submit" className='border-2 px-3 py-1 rounded-lg mt-10 hover:bg-red-500 hover:scale-110 hover:ease-in-out ease-in-out duration-500'>Submit</button>
          </form>
          <div className='bg-white shadow-xl flex-1'>
            <h1 className='text-2xl text-center'>Result Message</h1>
            {decryptedMessage && (
              <div className='flex items-center flex-col'>
                <p>message is: {decryptedMessage}</p>
              </div>
            )}
          </div>
        </>
      ) : (
        <>
          <form onSubmit={handleSubmit} className='w-[50%] flex flex-col justify-center items-center h-screen'>
            <div className='w-[auto]flex justify-center'>
            {image ? (
              <img src={URL.createObjectURL(image)} className='p-5' />
            ) : (
            <div {...getRootProps()} className='border-2 p-10 rounded-md cursor-pointer'>
              <input {...getInputProps()} />

              {isDragActive ? (
                <p>Drop the image here...</p>
              ) : (
                <p>Drag & drop an image here, or click to select a file</p>
              )}
            </div>

            )}
            </div>
            <textarea name="pesan" id="pesan" rows="4" cols="50" className='border-2 mt-10' value={message} onChange={handleMessageChange}></textarea>
            <button type="submit" className='border-2 px-3 py-1 rounded-lg mt-10 hover:bg-red-500 hover:scale-110 hover:ease-in-out ease-in-out duration-500'>Submit</button>
          </form>

          <div className='bg-white shadow-xl flex-1'>
            <h1 className='text-2xl text-center'>Result Image</h1>
            {resultImageUrl && (
              <div className='flex items-center flex-col'>
                <img src={`http://localhost:5000${resultImageUrl}`} alt="Result" className='w-72 my-14' />
                <a href={`http://localhost:5000/static/uploads/hasil.png`} download="hasil.png">
                  <button>Download</button>
                </a>
                <p>Encryption Key: {encryptionKey}</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
