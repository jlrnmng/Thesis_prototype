from app import create_app

# Create app to trigger initialization (models, chroma client)
app = create_app()
print('INIT_DONE')
