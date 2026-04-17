from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from agent import build_graph, _content_to_text, AgentState, _setup_logging

app = Flask(__name__)
CORS(app)

# Configure logging using agent's logging setup
_setup_logging()
LOGGER = logging.getLogger("XanhSM")

# Initialize graph from agent
graph = build_graph()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'JSON payload is required'}), 400

        user_message = data.get('message', '')
        thread_id = data.get('thread_id', 'default-session')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Invoke the graph with config
        config = {"configurable": {"thread_id": thread_id}}
        result: AgentState = graph.invoke(
            {"messages": [("human", user_message)]},
            config=config
        )
        final_msg = result["messages"][-1]
        
        # Extract response
        response_text = _content_to_text(getattr(final_msg, 'content', ''))
        
        return jsonify({
            'response': response_text,
            'status': 'success',
            'thread_id': thread_id
        })
    
    except Exception as e:
        LOGGER.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
