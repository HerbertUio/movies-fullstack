// src/AppContent.jsx
import React, { useState, useEffect, useContext } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import CategoryList from './components/CategoryList';
import MovieList from './components/MovieList';
import EditMovieModal from './components/EditMovieModal';
import AddMovieModal from './components/AddMovieModal';
import AddMovieButton from './components/AddMovieButton';
import CategoryManagement from './components/CategoryManagement';
import { AuthContext } from './context/AuthContext';
import axios from './api/axiosConfig';

function AppContent() {
  const { auth } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  const [movies, setMovies] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingMovie, setEditingMovie] = useState(null);
  const [addingMovie, setAddingMovie] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  // Redirigir a la página principal al cargar la aplicación si la ruta no es '/'
  useEffect(() => {
    if (location.pathname !== '/') {
      navigate('/');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (auth) {
      fetchMovies();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, selectedCategory]);

  const fetchMovies = async () => {
    try {
      let response;
      if (searchTerm) {
        response = await axios.get(`/buscarPelicula/${searchTerm}`);
      } else if (selectedCategory) {
        response = await axios.get(`/obtenerPeliculasEnCategoria/${selectedCategory}`);
      } else {
        response = await axios.get('/obtenerPeliculas');
      }
      setMovies(response.data);
    } catch (error) {
      console.error('Error al obtener las películas:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/borrarPelicula/${id}`);
      setMovies(movies.filter((movie) => movie.id !== id));
    } catch (error) {
      console.error('Error al eliminar la película:', error);
    }
  };

  const handleEdit = (movie) => {
    setEditingMovie(movie);
  };

  const handleMovieUpdated = () => {
    fetchMovies();
    setEditingMovie(null);
  };

  const handleMovieAdded = () => {
    fetchMovies();
    setAddingMovie(false);
  };

  return (
    <div className="bg-black min-h-screen">
      <Navbar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      <div>
        <Routes>
          <Route
            path="/"
            element={
              <>
                <CategoryList
                  selectedCategory={selectedCategory}
                  setSelectedCategory={setSelectedCategory}
                />
                <MovieList movies={movies} onDelete={handleDelete} onEdit={handleEdit} />
                {auth.rol.toLowerCase() === 'administrador' && (
                  <>
                    <AddMovieButton onAdd={() => setAddingMovie(true)} />
                    {addingMovie && (
                      <AddMovieModal
                        onClose={() => setAddingMovie(false)}
                        onMovieAdded={handleMovieAdded}
                      />
                    )}
                    {editingMovie && (
                      <EditMovieModal
                        movie={editingMovie}
                        onClose={() => setEditingMovie(null)}
                        onMovieUpdated={handleMovieUpdated}
                      />
                    )}
                  </>
                )}
              </>
            }
          />
          <Route
            path="/gestion-categorias"
            element={
              auth.rol.toLowerCase() === 'administrador' ? (
                <CategoryManagement />
              ) : (
                <div className="text-white p-4">No tienes acceso a esta página.</div>
              )
            }
          />
          {/* Puedes agregar más rutas aquí */}
        </Routes>
      </div>
    </div>
  );
}

export default AppContent;
