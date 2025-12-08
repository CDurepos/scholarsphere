/**
 * @author Clayton Durepos
 */

import Header from '../../components/Header';
import styles from './Institutions.module.css';

/**
 * Institutions search page - placeholder
 */
function Institutions() {
  return (
    <div className={styles['search-container']}>
      <Header />
      
      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          <h2 className={styles['search-title']}>Search Institutions</h2>
          <div className={styles['search-placeholder']}>
            <p>Institutions search coming soon...</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Institutions;
