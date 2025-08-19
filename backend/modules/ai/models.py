from app import db
from datetime import datetime
# Use db.JSON for SQLite compatibility

class AIModel(db.Model):
    """AI/ML models for different use cases"""
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(100), nullable=False)  # classification, regression, clustering, anomaly_detection
    use_case = db.Column(db.String(100), nullable=False)  # churn_prediction, sales_forecast, fraud_detection, demand_forecast
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='training')  # training, active, inactive, deprecated
    accuracy = db.Column(db.Float, default=0.0)
    precision = db.Column(db.Float, default=0.0)
    recall = db.Column(db.Float, default=0.0)
    f1_score = db.Column(db.Float, default=0.0)
    model_file_path = db.Column(db.String(500))
    model_parameters = db.Column(db.JSON)  # Store model hyperparameters
    training_data_info = db.Column(db.JSON)  # Store training data statistics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployed_at = db.Column(db.DateTime)

class Prediction(db.Model):
    """AI predictions and forecasts"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    entity_id = db.Column(db.Integer)  # ID of the entity being predicted (customer, product, etc.)
    entity_type = db.Column(db.String(100), nullable=False)  # customer, product, transaction, etc.
    prediction_type = db.Column(db.String(100), nullable=False)  # churn, sales, fraud, demand
    prediction_date = db.Column(db.DateTime, nullable=False)
    prediction_horizon = db.Column(db.Integer)  # Days into the future
    predicted_value = db.Column(db.Float)
    confidence_score = db.Column(db.Float, default=0.0)
    prediction_data = db.Column(db.JSON)  # Store input features and prediction details
    actual_value = db.Column(db.Float)  # For validation
    accuracy = db.Column(db.Float)  # For validation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    model = db.relationship('AIModel', foreign_keys=[model_id])

class AnomalyDetection(db.Model):
    """Anomaly detection results"""
    __tablename__ = 'anomaly_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    entity_id = db.Column(db.Integer)
    entity_type = db.Column(db.String(100), nullable=False)
    anomaly_type = db.Column(db.String(100), nullable=False)  # transaction, behavior, pattern
    detection_date = db.Column(db.DateTime, nullable=False)
    anomaly_score = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, default=0.95)
    is_anomaly = db.Column(db.Boolean, default=False)
    severity = db.Column(db.String(20), default='low')  # low, medium, high, critical
    description = db.Column(db.Text)
    anomaly_data = db.Column(db.JSON)  # Store anomaly details
    status = db.Column(db.String(50), default='detected')  # detected, reviewed, resolved, false_positive
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    model = db.relationship('AIModel', foreign_keys=[model_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class RPAWorkflow(db.Model):
    """Robotic Process Automation workflows"""
    __tablename__ = 'rpa_workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    workflow_type = db.Column(db.String(100), nullable=False)  # ap_automation, po_matching, data_entry, report_generation
    status = db.Column(db.String(50), default='draft')  # draft, active, inactive, error
    workflow_config = db.Column(db.JSON)  # Store workflow configuration
    triggers = db.Column(db.JSON)  # Store trigger conditions
    steps = db.Column(db.JSON)  # Store workflow steps
    error_handling = db.Column(db.JSON)  # Store error handling rules
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = db.Column(db.DateTime)

class RPAExecution(db.Model):
    """RPA workflow executions"""
    __tablename__ = 'rpa_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('rpa_workflows.id'), nullable=False)
    execution_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='running')  # running, completed, failed, cancelled
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Float)
    input_data = db.Column(db.JSON)  # Store input data
    output_data = db.Column(db.JSON)  # Store output data
    error_message = db.Column(db.Text)
    execution_log = db.Column(db.JSON)  # Store execution steps and logs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = db.relationship('RPAWorkflow', foreign_keys=[workflow_id])

class AIConversation(db.Model):
    """AI conversation history"""
    __tablename__ = 'ai_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    conversation_type = db.Column(db.String(100), default='general')  # general, support, analysis, automation
    context = db.Column(db.JSON)  # Store conversation context
    status = db.Column(db.String(50), default='active')  # active, closed, archived
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    messages = db.relationship('AIMessage', backref='conversation', lazy=True)

class AIMessage(db.Model):
    """Individual messages in AI conversations"""
    __tablename__ = 'ai_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('ai_conversations.id'), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='text')  # text, image, file, chart
    message_metadata = db.Column(db.JSON)  # Store message metadata
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIPrediction(db.Model):
    __tablename__ = 'ai_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    prediction_type = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIInsight(db.Model):
    __tablename__ = 'ai_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    insight_type = db.Column(db.String(100), nullable=False)
    impact_score = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    recommendation_type = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(50), default='Medium')
    implementation_status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataPipeline(db.Model):
    """Data pipelines for AI/ML"""
    __tablename__ = 'data_pipelines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    pipeline_type = db.Column(db.String(100), nullable=False)  # etl, feature_engineering, model_training, inference
    status = db.Column(db.String(50), default='active')  # active, inactive, error
    schedule = db.Column(db.String(100))  # Cron expression for scheduling
    source_config = db.Column(db.JSON)  # Store source configuration
    transformation_config = db.Column(db.JSON)  # Store transformation rules
    destination_config = db.Column(db.JSON)  # Store destination configuration
    dependencies = db.Column(db.JSON)  # Store pipeline dependencies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = db.Column(db.DateTime)

class PipelineExecution(db.Model):
    """Data pipeline executions"""
    __tablename__ = 'pipeline_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('data_pipelines.id'), nullable=False)
    execution_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='running')  # running, completed, failed, cancelled
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Float)
    records_processed = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    execution_log = db.Column(db.JSON)  # Store execution details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pipeline = db.relationship('DataPipeline', foreign_keys=[pipeline_id])

class ModelPerformance(db.Model):
    """AI model performance metrics"""
    __tablename__ = 'model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    evaluation_date = db.Column(db.DateTime, nullable=False)
    metric_type = db.Column(db.String(100), nullable=False)  # accuracy, precision, recall, f1, mse, mae
    metric_value = db.Column(db.Float, nullable=False)
    dataset_type = db.Column(db.String(50), default='test')  # train, validation, test
    evaluation_data = db.Column(db.JSON)  # Store evaluation details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    model = db.relationship('AIModel', foreign_keys=[model_id])

class AIConfiguration(db.Model):
    """AI system configuration"""
    __tablename__ = 'ai_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(200), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(50), default='string')  # string, number, boolean, json
    description = db.Column(db.Text)
    category = db.Column(db.String(100), default='general')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User model is defined in core.models
