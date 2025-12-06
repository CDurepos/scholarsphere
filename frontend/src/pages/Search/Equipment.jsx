import Header from '../../components/Header';
import styles from './Equipment.module.css';

/**
 * Equipment search page - placeholder
 */
function Equipment() {
  return (
    <div className={styles['search-container']}>
      <Header />
      
      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          <h2 className={styles['search-title']}>Search Equipment</h2>
          <div className={styles['search-placeholder']}>
            <p>Equipment search coming soon...</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Equipment;
