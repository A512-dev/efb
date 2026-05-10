import { useEffect, useState } from "react";
import apiClient from "../services/apiClient";

const Users=()=> {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    apiClient.get("/users")
      .then(res => setUsers(res.data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div>
      <h2>Users</h2>
      {users.map(u => (
        <div key={u.id}>{u.name}</div>
      ))}
    </div>
  );
}

export default Users;
