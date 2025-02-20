// src/components/MovieList.jsx
import React from 'react';
import MovieCard from './MovieCard';

function MovieList({ movies, onDelete, onEdit }) {
  return (
    <div className="p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {movies.map((movie) => (
        <MovieCard key={movie.id} movie={movie} onDelete={onDelete} onEdit={onEdit} />
      ))}
    </div>
  );
}

export default MovieList;
