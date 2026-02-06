import axios from 'axios';

// API基础配置 - 加上/mac/前缀，确保Nginx能正确代理
const API_BASE_URL = '/mac';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 获取批次列表
export const getLotList = async () => {
  try {
    return await api.get('/api/v1/lot');
  } catch (error) {
    return [];
  }
};

// 获取产品列表
export const getProductList = async () => {
  try {
    return await api.get('/api/v1/product');
  } catch (error) {
    return [];
  }
};

// 获取缺陷代码列表
export const getReasonCodeList = async () => {
  try {
    return await api.get('/api/v1/reasoncode');
  } catch (error) {
    return [];
  }
};

// 获取初始化数据
export const getInitData = async () => {
  try {
    return await api.get('/api/v1/init-data');
  } catch (error) {
    return {};
  }
};

// 获取产品布局数据
export const getProductLayout = async (productspecname) => {
  try {
    return await api.get(`/api/v1/product/${productspecname}/layout`);
  } catch (error) {
    return {};
  }
};

// 获取玻璃列表
export const getGlassList = async (lotname) => {
  try {
    const response = await api.get(`/api/v1/lots/${lotname}/glasses`);
    // 将后端返回的glassid字段映射为前端期望的id字段
    return response.map(glass => ({
      ...glass,
      id: glass.glassid
    }));
  } catch (error) {
    return [];
  }
};

// 获取Glass缺陷记录
export const getDefects = async (glassId, processOperationName = '', isHistorical = false, startTime = '', endTime = '', machinename = null, defect_code = null) => {
  try {
    // 构建查询参数
    const params = {};
    if (processOperationName) {
      // 如果是数组，转换为逗号分隔字符串
      params.processoperationname = Array.isArray(processOperationName) ? processOperationName.join(',') : processOperationName;
    }
    
    // 如果是历史数据查询，添加时间参数
    if (isHistorical) {
      if (startTime) {
        params.start_time = startTime;
      }
      if (endTime) {
        params.end_time = endTime;
      }
      if (machinename && machinename.length > 0) {
        // 如果是数组，转换为逗号分隔字符串
        params.machinename = Array.isArray(machinename) ? machinename.join(',') : machinename;
      }
      if (defect_code && defect_code.length > 0) {
        // 如果是数组，转换为逗号分隔字符串
        params.defect_code = Array.isArray(defect_code) ? defect_code.join(',') : defect_code;
      }
    }
    
    // 根据是否为历史数据选择不同的API端点
    const endpoint = isHistorical 
      ? `/api/v1/historical/glasses/${glassId}/defects`
      : `/api/v1/glasses/${glassId}/defects`;
    
    return await api.get(endpoint, { params });
  } catch (error) {
    return [];
  }
};

// 获取历史Glass缺陷记录
export const getHistoricalDefects = async (glassId, processOperationName = '', startTime = '', endTime = '', machinename = null, defect_code = null) => {
  return getDefects(glassId, processOperationName, true, startTime, endTime, machinename, defect_code);
};

// 根据Lot获取所有Glass的缺陷记录
export const getDefectsByLot = async (lotname, processOperationName = '') => {
  try {
    // 构建查询参数
    const params = {};
    if (processOperationName) {
      params.processoperationname = processOperationName;
    }
    return await api.get(`/api/v1/lots/${lotname}/defects`, { params });
  } catch (error) {
    return [];
  }
};

// 根据Lot获取该批次下所有工序站点名称
export const getProcessOperationsByLot = async (lotname) => {
  try {
    return await api.get(`/api/v1/lots/${lotname}/process-operations`);
  } catch (error) {
    return [];
  }
};

// 保存缺陷记录
export const saveDefectRecord = async (defectRecord) => {
  // 转换前端数据格式为后端期望的格式
  const formattedDefect = {
    uuid: defectRecord.uuid || defectRecord.uid || `defect-${Date.now()}`, // 优先使用uuid，其次是uid，最后生成新的
    glass_id: defectRecord.glassId || defectRecord.id || defectRecord.glass_id, // 确保有glass_id，支持glass_id字段
    lotname: defectRecord.lotname,
    productrequestname: defectRecord.productrequestname,
    product_id: defectRecord.product_id || defectRecord.productspecname, // 确保有product_id
    defect_code: defectRecord.code || defectRecord.defect_code || '', // code -> defect_code，支持defect_code字段，提供默认值
    defect_type: defectRecord.type || defectRecord.defect_type || 'point', // type -> defect_type，支持defect_type字段，提供默认值
    geom_data: defectRecord.path || defectRecord.geom_data || (defectRecord.x && defectRecord.y ? [[defectRecord.x, defectRecord.y]] : undefined), // 转换为geom_data格式，支持直接从geom_data字段获取值
    panel_id: defectRecord.panelId || defectRecord.panel_id, // panelId -> panel_id
    is_symmetry: (() => {
      const value = defectRecord.isSymmetry !== undefined ? defectRecord.isSymmetry : defectRecord.is_symmetry;
      // 如果是字符串，直接比较是否为'Y'，否则使用布尔值判断
      return typeof value === 'string' ? (value === 'Y' ? 'Y' : 'N') : (value ? 'Y' : 'N');
    })(), // isSymmetry -> is_symmetry, support both camelCase and snake_case
    remark: defectRecord.remark,
    operator_id: defectRecord.operator_id,
    machinename: defectRecord.machinename,
    processoperationname: defectRecord.processoperationname,
    inspection_type: defectRecord.inspection_type || defectRecord.inspectionType || '首检', // 添加inspection_type字段，支持两种命名方式
    inspector: defectRecord.inspector // 添加inspector字段，确保检测人员信息正确传递
  };
  
  // 发送请求，使用完整的/api/v1前缀
  return await api.post('/api/v1/defect/save', formattedDefect);
};

// 查询缺陷记录
export const queryDefectRecords = async (queryParams) => {
  try {
    return await api.get('/api/v1/defects/query', { params: queryParams });
  } catch (error) {
    return {
      records: [],
      total: 0,
      page: queryParams?.page || 1,
      pageSize: queryParams?.pageSize || 10
    };
  }
};

// 根据CST或Lot获取关联信息
export const getRelatedInfoByCstOrLot = async ({ cst, lot }) => {
  try {
    return await api.get('/api/v1/related-info', { params: { cst, lot } });
  } catch (error) {
    return {};
  }
};

// 根据OPER过滤选项
export const filterOptionsByOper = async (oper) => {
  try {
    return await api.get('/api/v1/filter-options', { params: { oper } });
  } catch (error) {
    return {};
  }
};

// 根据IP地址获取匹配的Machine
export const getMachineByIp = async () => {
  try {
    return await api.get('/api/v1/machine-by-ip');
  } catch (error) {
    return {};
  }
};

// 验证userrole权限
export const checkPermission = async (userrole) => {
  try {
    return await api.get('/api/v1/auth/check-permission', { params: { userrole } });
  } catch (error) {
    console.error('权限验证失败:', error);
    return { allowed: false };
  }
};

// 删除缺陷记录
export const deleteDefectRecord = async (uuid) => {
  try {
    return await api.delete(`/api/v1/defect/${uuid}`);
  } catch (error) {
    throw error;
  }
};

export default api;