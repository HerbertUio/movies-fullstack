import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import axios from '../api/axiosConfig';

function MovieCard({ movie, onDelete, onEdit }) {
  const { auth } = useContext(AuthContext);
  const [categoryName, setCategoryName] = useState('');

  useEffect(() => {
    fetchCategoryName();
  }, []);

  const fetchCategoryName = async () => {
    if (movie.categoria_id) {
      try {
        const response = await axios.get(`/obtenerCategoria/${movie.categoria_id}`);
        setCategoryName(response.data.nombre);
      } catch (error) {
        console.error('Error al obtener el nombre de la categoría:', error);
        setCategoryName('Sin Categoría');
      }
    } else {
      setCategoryName('Sin Categoría');
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
      {movie.rutaImagen ? (
        <img
          src={`http://localhost:5000${movie.rutaImagen}`}
          alt={movie.nombre}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 flex items-center justify-center bg-gray-700 text-gray-400">
          Sin imagen
        </div>
      )}
      <div className="p-4">
        <h3 className="text-xl font-bold text-white mb-2">{movie.nombre}</h3>
        <p className="text-gray-300 text-sm mb-2">{movie.descripcion}</p>
        <p className="text-gray-400 text-sm mb-2">Duración: {movie.duracion} minutos</p>
        <p className="text-gray-400 text-sm mb-4">Categoría: {categoryName}</p>
        {auth.rol.toLowerCase() === 'administrador' && (
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit(movie)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md"
            >
              Editar
            </button>
            <button
              onClick={() => onDelete(movie.id)}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-md"
            >
              Eliminar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default MovieCard;
