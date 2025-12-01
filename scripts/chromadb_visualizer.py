#!/usr/bin/env python3
"""
ChromaDB Visualization Tool
Creates 2D and 3D visualizations of embeddings stored in ChromaDB using seaborn and matplotlib.
Supports clustering analysis, similarity mapping, and dimensional reduction visualization.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chromadb
from chromadb.utils import embedding_functions
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ChromaDBVisualizer:
    def __init__(self, chroma_path="chroma_storage"):
        """Initialize the ChromaDB visualizer"""
        self.chroma_path = chroma_path
        self.client = None
        self.collections_data = {}
        self.output_dir = "visualizations"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        self._init_chroma_client()
    
    def _init_chroma_client(self):
        """Initialize ChromaDB client with proper embedding function"""
        try:
            # Create embedding function to avoid warnings
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Initialize client with correct API
            self.client = chromadb.Client(settings=chromadb.config.Settings(
                chroma_db_impl='duckdb+parquet',
                persist_directory=self.chroma_path
            ))
            
            print(f"✅ Connected to ChromaDB at: {self.chroma_path}")
            
        except Exception as e:
            print(f"❌ Failed to connect to ChromaDB: {e}")
            sys.exit(1)
    
    def load_collections_data(self):
        """Load data from all ChromaDB collections"""
        try:
            collections = self.client.list_collections()
            
            for collection in collections:
                collection_name = collection.name
                print(f"📊 Loading data from collection: {collection_name}")
                
                # Get collection with embedding function
                coll = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn
                )
                
                # Get all data from collection
                data = coll.get(include=['embeddings', 'metadatas', 'documents'])
                
                if data['ids']:
                    self.collections_data[collection_name] = {
                        'ids': data['ids'],
                        'embeddings': np.array(data['embeddings']),
                        'metadatas': data['metadatas'],
                        'documents': data['documents'],
                        'count': len(data['ids'])
                    }
                    print(f"  ✅ Loaded {len(data['ids'])} items")
                else:
                    print(f"  ⚠️ Collection {collection_name} is empty")
                    
        except Exception as e:
            print(f"❌ Error loading collections: {e}")
            return False
        
        return True
    
    def create_combined_dataset(self):
        """Combine all collections into a single dataset for analysis"""
        all_embeddings = []
        all_labels = []
        all_metadata = []
        all_texts = []
        
        for collection_name, data in self.collections_data.items():
            embeddings = data['embeddings']
            count = data['count']
            
            all_embeddings.append(embeddings)
            all_labels.extend([collection_name] * count)
            all_metadata.extend(data['metadatas'])
            all_texts.extend(data['documents'])
        
        if not all_embeddings:
            print("⚠️ No data found in any collection")
            return None
        
        combined_embeddings = np.vstack(all_embeddings)
        
        # Create DataFrame
        df = pd.DataFrame({
            'collection': all_labels,
            'text': all_texts,
            'metadata': all_metadata
        })
        
        print(f"📈 Combined dataset: {len(df)} items from {len(self.collections_data)} collections")
        
        return combined_embeddings, df
    
    def apply_dimensionality_reduction(self, embeddings, method='pca', n_components=2):
        """Apply dimensionality reduction techniques"""
        print(f"🔄 Applying {method.upper()} dimensionality reduction...")
        
        if method.lower() == 'pca':
            reducer = PCA(n_components=n_components, random_state=42)
        elif method.lower() == 'tsne':
            reducer = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(embeddings)-1))
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Standardize embeddings
        scaler = StandardScaler()
        embeddings_scaled = scaler.fit_transform(embeddings)
        
        # Apply reduction
        reduced_embeddings = reducer.fit_transform(embeddings_scaled)
        
        if method.lower() == 'pca':
            variance_ratio = reducer.explained_variance_ratio_
            print(f"  📊 Explained variance: {variance_ratio.sum():.3f}")
        
        return reduced_embeddings
    
    def perform_clustering(self, embeddings, method='kmeans', n_clusters=None):
        """Perform clustering on embeddings"""
        print(f"🎯 Performing {method} clustering...")
        
        # Standardize embeddings
        scaler = StandardScaler()
        embeddings_scaled = scaler.fit_transform(embeddings)
        
        if method.lower() == 'kmeans':
            if n_clusters is None:
                # Estimate optimal clusters using elbow method
                n_clusters = min(8, max(2, len(embeddings) // 10))
            
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            
        elif method.lower() == 'dbscan':
            clusterer = DBSCAN(eps=0.5, min_samples=2)
            
        else:
            raise ValueError(f"Unsupported clustering method: {method}")
        
        cluster_labels = clusterer.fit_predict(embeddings_scaled)
        
        n_clusters_found = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        print(f"  🎯 Found {n_clusters_found} clusters")
        
        return cluster_labels
    
    def create_2d_visualizations(self, embeddings, df):
        """Create 2D visualizations using seaborn and matplotlib"""
        print("🎨 Creating 2D visualizations...")
        
        # 1. PCA 2D visualization
        pca_2d = self.apply_dimensionality_reduction(embeddings, 'pca', 2)
        df_pca = df.copy()
        df_pca['PCA1'] = pca_2d[:, 0]
        df_pca['PCA2'] = pca_2d[:, 1]
        
        # 2. t-SNE 2D visualization
        tsne_2d = self.apply_dimensionality_reduction(embeddings, 'tsne', 2)
        df_tsne = df.copy()
        df_tsne['TSNE1'] = tsne_2d[:, 0]
        df_tsne['TSNE2'] = tsne_2d[:, 1]
        
        # 3. Add clustering information
        clusters_kmeans = self.perform_clustering(embeddings, 'kmeans')
        clusters_dbscan = self.perform_clustering(embeddings, 'dbscan')
        
        df_pca['KMeans_Cluster'] = clusters_kmeans
        df_pca['DBSCAN_Cluster'] = clusters_dbscan
        df_tsne['KMeans_Cluster'] = clusters_kmeans
        df_tsne['DBSCAN_Cluster'] = clusters_dbscan
        
        # Create comprehensive 2D plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # PCA plots
        sns.scatterplot(data=df_pca, x='PCA1', y='PCA2', hue='collection', 
                       s=100, alpha=0.7, ax=axes[0,0])
        axes[0,0].set_title('PCA - Collections', fontsize=14, fontweight='bold')
        axes[0,0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        sns.scatterplot(data=df_pca, x='PCA1', y='PCA2', hue='KMeans_Cluster', 
                       palette='Set1', s=100, alpha=0.7, ax=axes[0,1])
        axes[0,1].set_title('PCA - K-Means Clustering', fontsize=14, fontweight='bold')
        axes[0,1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        sns.scatterplot(data=df_pca, x='PCA1', y='PCA2', hue='DBSCAN_Cluster', 
                       palette='Set2', s=100, alpha=0.7, ax=axes[0,2])
        axes[0,2].set_title('PCA - DBSCAN Clustering', fontsize=14, fontweight='bold')
        axes[0,2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # t-SNE plots
        sns.scatterplot(data=df_tsne, x='TSNE1', y='TSNE2', hue='collection', 
                       s=100, alpha=0.7, ax=axes[1,0])
        axes[1,0].set_title('t-SNE - Collections', fontsize=14, fontweight='bold')
        axes[1,0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        sns.scatterplot(data=df_tsne, x='TSNE1', y='TSNE2', hue='KMeans_Cluster', 
                       palette='Set1', s=100, alpha=0.7, ax=axes[1,1])
        axes[1,1].set_title('t-SNE - K-Means Clustering', fontsize=14, fontweight='bold')
        axes[1,1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        sns.scatterplot(data=df_tsne, x='TSNE1', y='TSNE2', hue='DBSCAN_Cluster', 
                       palette='Set2', s=100, alpha=0.7, ax=axes[1,2])
        axes[1,2].set_title('t-SNE - DBSCAN Clustering', fontsize=14, fontweight='bold')
        axes[1,2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/chromadb_2d_visualizations.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return df_pca, df_tsne
    
    def create_3d_visualizations(self, embeddings, df):
        """Create 3D visualizations using plotly"""
        print("🎨 Creating 3D visualizations...")
        
        # 3D PCA
        pca_3d = self.apply_dimensionality_reduction(embeddings, 'pca', 3)
        
        # 3D t-SNE
        tsne_3d = self.apply_dimensionality_reduction(embeddings, 'tsne', 3)
        
        # Add clustering
        clusters = self.perform_clustering(embeddings, 'kmeans')
        
        # Create 3D PCA plot
        fig_pca = px.scatter_3d(
            x=pca_3d[:, 0], 
            y=pca_3d[:, 1], 
            z=pca_3d[:, 2],
            color=df['collection'],
            title="3D PCA Visualization of ChromaDB Embeddings",
            labels={'x': 'PC1', 'y': 'PC2', 'z': 'PC3'},
            hover_data={'collection': df['collection'].values}
        )
        fig_pca.update_traces(marker_size=8)
        fig_pca.write_html(f"{self.output_dir}/chromadb_3d_pca.html")
        
        # Create 3D t-SNE plot
        fig_tsne = px.scatter_3d(
            x=tsne_3d[:, 0], 
            y=tsne_3d[:, 1], 
            z=tsne_3d[:, 2],
            color=df['collection'],
            title="3D t-SNE Visualization of ChromaDB Embeddings",
            labels={'x': 'TSNE1', 'y': 'TSNE2', 'z': 'TSNE3'},
            hover_data={'collection': df['collection'].values}
        )
        fig_tsne.update_traces(marker_size=8)
        fig_tsne.write_html(f"{self.output_dir}/chromadb_3d_tsne.html")
        
        # Create clustering 3D plot
        fig_cluster = px.scatter_3d(
            x=pca_3d[:, 0], 
            y=pca_3d[:, 1], 
            z=pca_3d[:, 2],
            color=clusters.astype(str),
            title="3D PCA with K-Means Clustering",
            labels={'x': 'PC1', 'y': 'PC2', 'z': 'PC3'},
            hover_data={'collection': df['collection'].values}
        )
        fig_cluster.update_traces(marker_size=8)
        fig_cluster.write_html(f"{self.output_dir}/chromadb_3d_clustering.html")
        
        print("📁 3D visualizations saved as HTML files")
    
    def create_similarity_heatmap(self, embeddings, df):
        """Create similarity heatmaps"""
        print("🔥 Creating similarity heatmaps...")
        
        # Sample if too many embeddings (for performance)
        if len(embeddings) > 100:
            indices = np.random.choice(len(embeddings), 100, replace=False)
            sample_embeddings = embeddings[indices]
            sample_df = df.iloc[indices].reset_index(drop=True)
        else:
            sample_embeddings = embeddings
            sample_df = df
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(sample_embeddings)
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
        
        sns.heatmap(similarity_matrix, 
                   mask=mask,
                   annot=False, 
                   cmap='RdYlBu_r', 
                   center=0,
                   square=True,
                   cbar_kws={'label': 'Cosine Similarity'})
        
        plt.title('Cosine Similarity Heatmap of ChromaDB Embeddings', 
                 fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/chromadb_similarity_heatmap.png", dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_collection_analysis(self):
        """Create collection-specific analysis"""
        print("📊 Creating collection analysis...")
        
        # Collection statistics
        stats_data = []
        for name, data in self.collections_data.items():
            embeddings = data['embeddings']
            stats_data.append({
                'Collection': name,
                'Count': data['count'],
                'Embedding_Dim': embeddings.shape[1] if len(embeddings) > 0 else 0,
                'Avg_Norm': np.mean(np.linalg.norm(embeddings, axis=1)) if len(embeddings) > 0 else 0,
                'Std_Norm': np.std(np.linalg.norm(embeddings, axis=1)) if len(embeddings) > 0 else 0
            })
        
        stats_df = pd.DataFrame(stats_data)
        
        # Create collection comparison plots
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Count comparison
        sns.barplot(data=stats_df, x='Collection', y='Count', ax=axes[0])
        axes[0].set_title('Document Count by Collection', fontweight='bold')
        
        # Average norm comparison
        sns.barplot(data=stats_df, x='Collection', y='Avg_Norm', ax=axes[1])
        axes[1].set_title('Average Embedding Norm by Collection', fontweight='bold')
        
        # Norm standard deviation
        sns.barplot(data=stats_df, x='Collection', y='Std_Norm', ax=axes[2])
        axes[2].set_title('Embedding Norm Standard Deviation', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/chromadb_collection_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Save statistics
        stats_df.to_csv(f"{self.output_dir}/chromadb_statistics.csv", index=False)
        print("📊 Collection statistics saved to CSV")
        
        return stats_df
    
    def generate_report(self, stats_df):
        """Generate a comprehensive analysis report"""
        print("📋 Generating analysis report...")
        
        report = f"""
# ChromaDB Visualization Report
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Database Overview
- **ChromaDB Path**: {self.chroma_path}
- **Total Collections**: {len(self.collections_data)}
- **Total Documents**: {sum(data['count'] for data in self.collections_data.values())}

## Collection Details
{stats_df.to_string(index=False)}

## Visualizations Generated
1. **2D Visualizations** (`chromadb_2d_visualizations.png`)
   - PCA and t-SNE plots
   - Collection groupings and clustering analysis
   
2. **3D Visualizations** (Interactive HTML files)
   - `chromadb_3d_pca.html`: 3D PCA visualization
   - `chromadb_3d_tsne.html`: 3D t-SNE visualization
   - `chromadb_3d_clustering.html`: 3D clustering analysis
   
3. **Similarity Analysis** (`chromadb_similarity_heatmap.png`)
   - Cosine similarity heatmap between embeddings
   
4. **Collection Analysis** (`chromadb_collection_analysis.png`)
   - Statistical comparison between collections

## Key Insights
- **Embedding Dimensions**: {stats_df['Embedding_Dim'].iloc[0] if len(stats_df) > 0 else 'N/A'}
- **Most Populated Collection**: {stats_df.loc[stats_df['Count'].idxmax(), 'Collection'] if len(stats_df) > 0 else 'N/A'}
- **Highest Average Norm**: {stats_df.loc[stats_df['Avg_Norm'].idxmax(), 'Collection'] if len(stats_df) > 0 else 'N/A'}

## Files Generated
- Static images: PNG format for reports and presentations
- Interactive plots: HTML format for detailed exploration
- Statistics: CSV format for further analysis
"""
        
        with open(f"{self.output_dir}/analysis_report.md", 'w') as f:
            f.write(report)
        
        print(f"📋 Analysis report saved to: {self.output_dir}/analysis_report.md")
    
    def run_complete_analysis(self):
        """Run the complete visualization analysis"""
        print("🚀 Starting ChromaDB Visualization Analysis")
        print("=" * 50)
        
        # Load data
        if not self.load_collections_data():
            return
        
        if not self.collections_data:
            print("❌ No data found in ChromaDB collections")
            return
        
        # Combine datasets
        result = self.create_combined_dataset()
        if result is None:
            return
        
        embeddings, df = result
        
        # Create visualizations
        self.create_2d_visualizations(embeddings, df)
        self.create_3d_visualizations(embeddings, df)
        self.create_similarity_heatmap(embeddings, df)
        
        # Collection analysis
        stats_df = self.create_collection_analysis()
        
        # Generate report
        self.generate_report(stats_df)
        
        print("\n✅ Analysis Complete!")
        print(f"📁 All visualizations saved to: {self.output_dir}/")
        print(f"📊 View 2D plots: {self.output_dir}/chromadb_2d_visualizations.png")
        print(f"🌐 View 3D plots: Open HTML files in browser")
        print(f"📋 Read report: {self.output_dir}/analysis_report.md")

def main():
    """Main function to run the visualization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize ChromaDB embeddings')
    parser.add_argument('--chroma-path', default='chroma_storage', 
                       help='Path to ChromaDB storage directory')
    parser.add_argument('--output-dir', default='visualizations',
                       help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    # Initialize visualizer
    visualizer = ChromaDBVisualizer(chroma_path=args.chroma_path)
    visualizer.output_dir = args.output_dir
    
    # Run analysis
    visualizer.run_complete_analysis()

if __name__ == "__main__":
    main()