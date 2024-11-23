import React from "react";
import "../styles/LandingPage/team.css";

const Team = () => {
  return (
    <div className="lp-team">
      <h2>Meet the Team</h2>
      <div className="team-members">
        <div className="team-member">
          <img src="team-member1.jpg" alt="Team Member 1" />
          <h3>Adarsh Singh</h3>
          <p>Role</p>
        </div>
        <div className="team-member">
          <img src="team-member2.jpg" alt="Team Member 2" />
          <h3>Anagha A Rao</h3>
          <p>Backend Developer</p>
        </div>
        <div className="team-member">
          <img src="team-member3.jpg" alt="Team Member 3" />
          <h3>Anjali Bhatkal</h3>
          <p>Frontend Developer</p>
        </div>
        <div className="team-member">
          <img src="team-member3.jpg" alt="Team Member 3" />
          <h3>Shiva Mani K</h3>
          <p>Role</p>
        </div>
      </div>
    </div>
  );
};

export default Team;
