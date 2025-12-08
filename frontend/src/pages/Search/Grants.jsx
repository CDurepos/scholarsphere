/**
 * @author Clayton Durepos
 */

import Header from '../../components/Header';
import styles from './Grants.module.css';

/**
 * Grants search page - placeholder
 */
function Grants() {
  return (
    <div className={styles['search-container']}>
      <Header />
      
      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          <h2 className={styles['search-title']}>Search Grants</h2>
          <div className={styles['search-placeholder']}>
            <p>Grants search coming soon...</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Grants;
