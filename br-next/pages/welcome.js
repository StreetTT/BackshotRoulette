import { useState } from 'react';
import { useRouter } from 'next/router';

const Landing = () => {
  const [name, setName] = useState('');
  const router = useRouter();


  const handleSubmit = (e) => {
    e.preventDefault();
    if (name) {
      console.log(name);
      
      // Send to server

      router.push('/game');
    }
  };

  return (
    <div className='welcomeContainer'>
      <div className='welcome'>
        <h1>Name: </h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
          />
          <button type="submit">Enter</button>
        </form>
      </div>
    </div>
  );
};

export default Landing;